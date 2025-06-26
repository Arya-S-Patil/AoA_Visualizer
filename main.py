import socket
import os
import threading
import time
import math
from flask import Flask, request, send_from_directory, jsonify
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision

# Load .env variables
load_dotenv()
token = os.getenv("INFLUXDB_TOKEN")
org = os.getenv("INFLUXDB_ORG")
bucket = os.getenv("BUCKET_UUDP")
url = os.getenv("INFLUXDB_HOST")

if not all([token, org, bucket, url]):
    raise EnvironmentError("Missing one or more required environment variables.")

print("Loaded env variables", flush=True)

# InfluxDB Client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()
print("[+] InfluxDB client ready", flush=True)

# Global state
drone_position = {"active": False, "x": 0, "y": 0, "z": 0}
latest_aoa = {}  # Live memory view of AoA data
recent_positions = []  # Stores last few tag positions with timestamp
latest_D = 2.0  # Default anchor distance

# Flask App
app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/position', methods=['POST'])
def update_position():
    global drone_position
    data = request.json
    try:
        if data.get("active"):
            drone_position.update({
                "x": float(data["x"]),
                "y": float(data["y"]),
                "z": float(data["z"]),
                "active": True
            })
            print(f"[UI] Activated logging at X={data['x']}, Y={data['y']}, Z={data['z']}", flush=True)
        else:
            drone_position["active"] = False
            print("[UI] Logging stopped by user", flush=True)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}, 400

@app.route('/latest')
def latest_data():
    return jsonify(latest_aoa)

@app.route('/grid')
def calculate_grid():
    global latest_D
    try:
        latest_D = float(request.args.get("D", 2.0))
        anchors = [(0, 0), (latest_D, 0)]
        azimuths = {}
        for mac, data in latest_aoa.items():
            azimuths[mac] = data["azimuth"]

        if len(azimuths) < 2:
            return {"error": "Need 2 peers with azimuth"}, 400

        peer_macs = list(azimuths.keys())[:2]  # Only take two peers
        az1 = azimuths[peer_macs[0]]
        az2 = azimuths[peer_macs[1]]

        def get_unit_vector(deg):
            theta = math.radians(deg)
            return math.sin(theta), math.cos(theta)

        x1, y1 = anchors[0]
        x2, y2 = anchors[1]
        dx1, dy1 = get_unit_vector(az1)
        dx2, dy2 = get_unit_vector(az2)

        denom = dx1 * dy2 - dy1 * dx2
        if abs(denom) < 1e-6:
            return {"error": "Angles result in nearly parallel lines"}, 400

        t1 = ((x2 - x1) * dy2 - (y2 - y1) * dx2) / denom
        tag_x = x1 + t1 * dx1
        tag_y = y1 + t1 * dy1

        # Store the result with timestamp
        recent_positions.append({"x": tag_x, "y": tag_y, "timestamp": time.time()})

        return {"x": tag_x, "y": tag_y, "from": peer_macs}

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/grid-history')
def get_grid_history():
    try:
        cutoff = time.time() - 5  # Keep points visible for 5 seconds
        valid_points = [p for p in recent_positions if p["timestamp"] >= cutoff]
        return jsonify({"points": valid_points, "D": latest_D})
    except Exception as e:
        return {"error": str(e)}, 500

def listen_udp():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5333
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print(f"[+] Listening for UDP packets on port {UDP_PORT}...", flush=True)
    except Exception as e:
        print(f"[!] Failed to bind socket: {e}", flush=True)
        return

    while True:
        try:
            data, addr = sock.recvfrom(2048)
            message = data.decode().strip()
            print(f"[UDP] {addr}: {message}", flush=True)

            if message.startswith("+UUDF:") and drone_position["active"]:
                parts = message.split(":")[1].split(",")
                if len(parts) < 7:
                    print("[!] Incomplete data, skipping", flush=True)
                    continue

                mac = parts[0]
                rssi = int(parts[1])
                azimuth = int(parts[2])
                elevation = int(parts[3])
                antenna = int(parts[4])
                channel = int(parts[5])
                peer_mac = parts[6].replace('"', '').strip()

                point = (
                    Point("uudp_packet")
                    .tag("mac", mac)
                    .tag("peer_mac", peer_mac)
                    .field("rssi", rssi)
                    .field("azimuth", azimuth)
                    .field("elevation", elevation)
                    .field("antenna", antenna)
                    .field("channel", channel)
                    .field("drone_x", drone_position["x"])
                    .field("drone_y", drone_position["y"])
                    .field("drone_z", drone_position["z"])
                    .time(time.time_ns(), WritePrecision.NS)
                )
                write_api.write(bucket=bucket, org=org, record=point)
                print("[+] Data written with drone position", flush=True)

                latest_aoa[peer_mac] = {
                    "azimuth": azimuth,
                    "elevation": elevation,
                    "timestamp": time.time()
                }

            else:
                print("[-] Ignored packet (inactive or invalid format)", flush=True)

        except Exception as e:
            print(f"[!] Error in UDP handler: {e}", flush=True)

# Launch UDP in background
threading.Thread(target=listen_udp, daemon=True).start()

# Run Flask
if __name__ == '__main__':
    try:
        print("[+] Starting Flask server on http://localhost:5000", flush=True)
        app.run(port=5000)
    except Exception as e:
        print(f"[!] Flask failed: {e}", flush=True)
