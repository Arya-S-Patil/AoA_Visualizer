import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read CSV
df = pd.read_csv(r"C:\Users\aryas\Desktop\Visualization\Experiment1(50).csv", skiprows=1, low_memory=False)
df.columns = df.columns.str.strip().str.lower()

# Anchors positions
anchors = {
    '20BA36977463': (0, 0, 0),
    '20BA369AFC6B': (3, 0, 0)
}

# Compute calculated azimuth & elevation
real_azimuths = []
real_elevations = []

for idx, row in df.iterrows():
    mac = row['peer_mac']
    ax, ay, az = anchors.get(mac, (np.nan, np.nan, np.nan))
    dx = row['drone_x'] - ax
    dy = row['drone_y'] - ay
    dz = row['drone_z'] - az

    azimuth_calc = np.degrees(np.arctan2(-dx, dy))
    azimuth_calc = -azimuth_calc

    azimuth_calc = (azimuth_calc + 180) % 360
    if azimuth_calc > 180:
        azimuth_calc -= 360

    elevation_calc = np.degrees(np.arctan2(dz, np.hypot(dx, dy)))

    real_azimuths.append(azimuth_calc)
    real_elevations.append(elevation_calc)

df['calculated_azimuth'] = real_azimuths
df['calculated_elevation'] = real_elevations

# 📥 User input
x0 = float(input("Enter drone_x: "))
y0 = float(input("Enter drone_y: "))
z0 = float(input("Enter drone_z: "))

df_point = df[
    (df['drone_x'] == x0) &
    (df['drone_y'] == y0) &
    (df['drone_z'] == z0)
]

if df_point.empty:
    print("⚠️ No data found for given coordinates.")
else:
    print(f"✅ Found {len(df_point)} records at ({x0}, {y0}, {z0})")

    for mac in df_point['peer_mac'].unique():
        sub = df_point[df_point['peer_mac'] == mac]

        exp_azimuths = sub['azimuth']
        calc_azimuths = sub['calculated_azimuth']
        exp_elevations = sub['elevation']
        calc_elevations = sub['calculated_elevation']

        # 📊 Azimuth Histogram
        plt.figure(figsize=(8,5))
        plt.hist(exp_azimuths, bins=10, alpha=0.7, label='Experimental Azimuths', color='skyblue', edgecolor='k')
        plt.axvline(x=calc_azimuths.iloc[0], color='orange', linestyle='--', linewidth=2,
                    label=f'Calculated Azimuth (Ground Truth: {calc_azimuths.iloc[0]:.1f})')
        plt.title(f"Azimuths @ ({x0},{y0},{z0}) | MAC: {mac}")
        plt.xlabel("Azimuth (degrees)")
        plt.ylabel("Count")
        plt.legend()
        plt.tight_layout()
        plt.show()

        # 📊 Elevation Histogram
        plt.figure(figsize=(8,5))
        plt.hist(exp_elevations, bins=10, alpha=0.7, label='Experimental Elevations', color='salmon', edgecolor='k')
        plt.axvline(x=calc_elevations.iloc[0], color='green', linestyle='--', linewidth=2,
                    label=f'Calculated Elevation (Ground Truth: {calc_elevations.iloc[0]:.1f})')
        plt.title(f"Elevations @ ({x0},{y0},{z0}) | MAC: {mac}")
        plt.xlabel("Elevation (degrees)")
        plt.ylabel("Count")
        plt.legend()
        plt.tight_layout()
        plt.show()
