// src/components/MapView.jsx
import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "../leafletFix.js";

const MAP_CENTER = [28.5355, 77.391];

// ── Fixes Leaflet blank-tile glitch + adds zoom control ──────────────────
function MapSetup() {
  const map = useMap();
  useEffect(() => {
    setTimeout(() => map.invalidateSize(), 150);
    L.control.zoom({ position: "topright" }).addTo(map);
  }, [map]);
  return null;
}

// ── Imperative marker API exposed via mapRef.current ─────────────────────
function MarkerController({ mapRef }) {
  const map = useMap();

  useEffect(() => {
    if (!mapRef) return;

    // Camera node — animated ping
    const camIcon = L.divIcon({
      className: "",
      iconSize: [0, 0],
      html: `
        <div style="position:relative;width:0;height:0">
          <div style="
            position:absolute;
            transform:translate(-50%,-50%);
            width:44px;height:44px;
            border:2px solid rgba(29,78,216,0.3);
            border-radius:50%;
            animation:camPing 2.8s ease-out infinite;
          "></div>
          <div style="
            position:absolute;
            transform:translate(-50%,-50%);
            width:15px;height:15px;
            background:white;
            border:3px solid #1d4ed8;
            border-radius:50%;
            box-shadow:0 2px 12px rgba(29,78,216,0.4);
            z-index:2;
          "></div>
        </div>
        <style>
          @keyframes camPing {
            0%  { transform:translate(-50%,-50%) scale(.4); opacity:.8; }
            100%{ transform:translate(-50%,-50%) scale(2.4); opacity:0; }
          }
        </style>
      `,
    });

    L.marker(MAP_CENTER, { icon: camIcon })
      .bindPopup(popupHTML("📷 Camera Node 1", "AETIS Surveillance Active", `${MAP_CENTER[0].toFixed(4)}, ${MAP_CENTER[1].toFixed(4)}`, "#1d4ed8"))
      .addTo(map);

    // Expose addMarker to parent via ref
    mapRef.current = {
      addMarker: ({ position, color, label, sublabel }) => {
        const icon = L.divIcon({
          className: "",
          iconSize: [0, 0],
          html: `<div style="
            position:absolute;
            transform:translate(-50%,-50%);
            width:14px;height:14px;
            background:${color};
            border:2.5px solid white;
            border-radius:50%;
            box-shadow:0 2px 10px ${color}88;
          "></div>`,
        });
        L.marker(position, { icon })
          .bindPopup(popupHTML(label, sublabel, null, color))
          .addTo(map);
      },
    };
  }, [map, mapRef]);

  return null;
}

function popupHTML(title, sub, mono, accentColor) {
  return `
    <div style="font-family:'DM Sans',sans-serif;padding:12px 14px;min-width:160px">
      <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:14px;margin-bottom:4px">${title}</div>
      ${sub  ? `<div style="font-size:12px;color:#64748b">${sub}</div>` : ""}
      ${mono ? `<div style="font-size:11px;color:${accentColor};margin-top:5px;font-family:'JetBrains Mono',monospace">${mono}</div>` : ""}
    </div>
  `;
}

// ── Component ─────────────────────────────────────────────────────────────
export default function MapView({ mapRef }) {
  return (
    <div className="map-panel">
      <div className="map-header">
        <div className="map-title">
          <div className="map-title-icon">🗺</div>
          Noida — Live Traffic View
        </div>
        <div className="map-tags">
          <div className="map-tag">
            <div className="map-tag-dot" style={{ background: "#1d4ed8" }} />
            Camera Node
          </div>
          <div className="map-tag">
            <div className="map-tag-dot" style={{ background: "#ef4444" }} />
            HIGH Severity
          </div>
          <div className="map-tag">
            <div className="map-tag-dot" style={{ background: "#f59e0b" }} />
            MEDIUM Severity
          </div>
        </div>
      </div>

      <div className="map-container">
        <MapContainer
          center={MAP_CENTER}
          zoom={15}
          style={{ height: "100%", width: "100%" }}
          zoomControl={false}
          attributionControl={false}
        >
          <MapSetup />
          <MarkerController mapRef={mapRef} />

          {/* Voyager tiles — clean, bright, professional */}
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
          />

        </MapContainer>
      </div>
    </div>
  );
}