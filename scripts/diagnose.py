import requests, os
from dotenv import load_dotenv
load_dotenv()

laptop_a = os.getenv("LAPTOP_A_IP", "192.168.1.101")
laptop_b = os.getenv("LAPTOP_B_IP", "192.168.1.102")

try:
    requests.get(f"http://{laptop_a}:5000/status", timeout=2)
    print("✓ Laptop A signal server")
except:
    print(f"✗ Laptop A ({laptop_a}) — is signal_server.py running?")

try:
    requests.get(f"http://{laptop_b}:5000/status", timeout=2)
    print("✓ Laptop B signal server")
except:
    print(f"✗ Laptop B ({laptop_b}) — is signal_server.py running?")