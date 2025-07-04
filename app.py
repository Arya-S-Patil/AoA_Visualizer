import pandas as pd
import matplotlib.pyplot as plt

# 📂 Read file
df = pd.read_csv(
    r"C:\Users\aryas\Desktop\Visualization\Experiment1(50).csv",
    low_memory=False,
    skiprows=1  # adjust if necessary!
)

# 🧹 Clean column names
df.columns = df.columns.str.strip().str.lower()
print("✅ Columns in CSV:", df.columns.tolist())

# 🧹 Convert to numeric as needed
for col in ['drone_x', 'drone_y', 'drone_z', 'rssi']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['peer_mac'] = df['peer_mac'].astype(str).str.strip()

# 📥 User input
fixed_drone_x = float(input("Enter fixed drone_x: "))
fixed_drone_z = float(input("Enter fixed drone_z: "))
fixed_peer_mac = input("Enter fixed peer_mac: ").strip()

print(f"🔍 Filtering for: X={fixed_drone_x}, Z={fixed_drone_z}, MAC={fixed_peer_mac}")

df_filtered = df[
    (df['drone_x'] == fixed_drone_x) &
    (df['drone_z'] == fixed_drone_z) &
    (df['peer_mac'] == fixed_peer_mac)
]

if df_filtered.empty:
    print("⚠️ No data for given parameters.")
    exit()

print(f"✅ Found {len(df_filtered)} rows after filtering.")

# 📊 Sort
df_filtered = df_filtered.sort_values('drone_y')

# 📈 Plot all RSSI vs Drone_Y
plt.figure(figsize=(12, 6))
plt.plot(
    df_filtered['drone_y'], 
    df_filtered['rssi'], 
    marker='o', linestyle='-', label='RSSI'
)

# 🔷 Compute and overlay average RSSI per drone_y
avg_rssi = df_filtered.groupby('drone_y')['rssi'].mean().reset_index()

plt.plot(
    avg_rssi['drone_y'], 
    avg_rssi['rssi'], 
    color='red', marker='x', linestyle='--', label='Average RSSI'
)

plt.xlabel("Drone Y")
plt.ylabel("RSSI")
plt.title(f"RSSI vs Drone_Y @ X={fixed_drone_x}, Z={fixed_drone_z}, MAC={fixed_peer_mac}")
plt.grid(True)
plt.legend()
plt.show()
