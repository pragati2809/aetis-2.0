# hardware/signal_client.py
# This file manages the WebSocket connections to the signal display laptops.
# Laptop 2 and Laptop 3 connect here and receive signal commands in real time.
 
from typing import List, Dict
from fastapi import WebSocket
import json, asyncio
 
class SignalConnectionManager:
    def __init__(self):
        # signal_id -> list of connected websockets
        self.connections: Dict[str, List[WebSocket]] = {
            "signal_1": [],
            "signal_2": [],
            "signal_3": [],
        }
        # current state of each signal
        self.states: Dict[str, str] = {
            "signal_1": "red",
            "signal_2": "red",
            "signal_3": "red",
        }
 
    async def connect(self, signal_id: str, ws: WebSocket):
        await ws.accept()
        if signal_id not in self.connections:
            self.connections[signal_id] = []
        self.connections[signal_id].append(ws)
        # Send current state immediately on connect
        await ws.send_text(json.dumps({
            "state": self.states.get(signal_id, "red"),
            "signal_id": signal_id
        }))
        print(f"Signal display connected: {signal_id} ({len(self.connections[signal_id])} clients)")
 
    def disconnect(self, signal_id: str, ws: WebSocket):
        if signal_id in self.connections:
            self.connections[signal_id].remove(ws)
 
    async def set_signal(self, signal_id: str, state: str):
        """Set signal state and broadcast to all connected display laptops."""
        self.states[signal_id] = state
        dead = []
        for ws in self.connections.get(signal_id, []):
            try:
                await ws.send_text(json.dumps({
                    "state": state,
                    "signal_id": signal_id
                }))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.connections[signal_id].remove(ws)
 
    """async def activate_green_corridor(self, corridor_plan: list):
        Schedule all signal changes with delays.
        for cmd in corridor_plan:
            asyncio.create_task(self._delayed_signal(
                cmd["signal_id"],
                cmd.get("delay_seconds", 0),
                cmd.get("duration", 18)
            ))
        #print("🟢 Sending GREEN to:", corridor)"""
    async def activate_green_corridor(self, corridor_plan: list):
        for cmd in corridor_plan:
            signal_id = cmd["signal_id"]

            print("🟢 Sending GREEN to:", signal_id)

            if signal_id in self.connections:
                for ws in self.connections[signal_id]:
                    await ws.send_json({
                        "action": "GREEN",
                        "signal_id": signal_id
                    })
 
    async def _delayed_signal(self, signal_id, delay, duration):
        await asyncio.sleep(delay)
        await self.set_signal(signal_id, "green")
        await asyncio.sleep(duration)
        await self.set_signal(signal_id, "red")
 
    async def reset_all(self):
        for signal_id in self.connections:
            await self.set_signal(signal_id, "red")
 
    def get_status(self):
        return self.states.copy()
 
# Singleton instance used throughout the app
signal_manager = SignalConnectionManager()
