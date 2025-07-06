import pandas as pd
import numpy as np

# Read CSV
df = pd.read_csv(r"C:\Users\aryas\Desktop\Visualization\Experiment1(50).csv", skiprows=1, low_memory=False)
df.columns = df.columns.str.strip().str.lower()

# Anchors positions
anchors = {
    '20BA36977463': (0, 0, 0),
    '20BA369AFC6B': (3, 0, 0)
}

real_azimuths = []
real_elevations = []

# Compute real angles: Forward = +Y, Flip = True
for idx, row in df.iterrows():
    mac = row['peer_mac']
    ax, ay, az = anchors.get(mac, (np.nan, np.nan, np.nan))
    dx = row['drone_x'] - ax
    dy = row['drone_y'] - ay
    dz = row['drone_z'] - az

    # Forward = +Y
    azimuth_real = np.degrees(np.arctan2(-dx, dy))
    # Flip
    azimuth_real = -azimuth_real

    # Normalize azimuth to [-180, 180]
    azimuth_real = (azimuth_real + 180) % 360
    if azimuth_real > 180:
        azimuth_real -= 360

    elevation_real = np.degrees(np.arctan2(dz, np.hypot(dx, dy)))

    real_azimuths.append(azimuth_real)
    real_elevations.append(elevation_real)

# Add to dataframe
df['real_azimuth'] = real_azimuths
df['real_elevation'] = real_elevations

# Select columns for output
output_df = df[['drone_x', 'drone_y', 'drone_z', 'peer_mac',
                'real_azimuth', 'azimuth', 'real_elevation', 'elevation']].copy()

output_csv = "angles_with_best_convention.csv"
output_df.to_csv(output_csv, index=False)
print(f"✅ Saved CSV: {output_csv}")

# Range comparison
print("\n📊 Range comparison (degrees):")
print(f"Real Azimuth:       {output_df['real_azimuth'].min():.1f} to {output_df['real_azimuth'].max():.1f}")
print(f"Experimental Azimuth: {output_df['azimuth'].min():.1f} to {output_df['azimuth'].max():.1f}")
print(f"Real Elevation:     {output_df['real_elevation'].min():.1f} to {output_df['real_elevation'].max():.1f}")
print(f"Experimental Elevation: {output_df['elevation'].min():.1f} to {output_df['elevation'].max():.1f}")
