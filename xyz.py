import pandas as pd
import numpy as np

# Read CSV
df = pd.read_csv(r"C:\Users\aryas\Desktop\Visualization\Experiment1(50).csv", skiprows=1, low_memory=False)
df.columns = df.columns.str.strip().str.lower()

# Define anchor MACs & positions
mac1 = '20BA36977463'
mac2 = '20BA369AFC6B'
anchor_positions = {
    mac1: np.array([0, 0, 0]),
    mac2: np.array([3, 0, 0])
}

# Split into two dataframes
df1 = df[df['peer_mac'] == mac1].copy().reset_index(drop=True)
df2 = df[df['peer_mac'] == mac2].copy().reset_index(drop=True)

# Add a synthetic 'time' index if none exists
df1['time_index'] = df1.index
df2['time_index'] = df2.index

# Merge by closest time_index (row number)
merged = pd.merge_asof(
    df1.sort_values('time_index'),
    df2.sort_values('time_index'),
    on='time_index',
    direction='nearest',
    suffixes=('_1', '_2')
)

records = []

for idx, row in merged.iterrows():
    # Drone position
    drone_x = row['drone_x_1']
    drone_y = row['drone_y_1']
    drone_z = row['drone_z_1']
    drone_pos = np.array([drone_x, drone_y, drone_z])

    # Anchor 1
    az1 = np.radians(row['azimuth_1'])
    el1 = np.radians(row['elevation_1'])
    rssi1 = row['rssi_1']
    pos1 = anchor_positions[mac1]

    dir1 = np.array([
        np.cos(el1) * np.sin(az1),
        np.cos(el1) * np.cos(az1),
        np.sin(el1)
    ])

    # Anchor 2
    az2 = np.radians(row['azimuth_2'])
    el2 = np.radians(row['elevation_2'])
    rssi2 = row['rssi_2']
    pos2 = anchor_positions[mac2]

    dir2 = np.array([
        np.cos(el2) * np.sin(az2),
        np.cos(el2) * np.cos(az2),
        np.sin(el2)
    ])

    # Solve closest point between two rays
    w0 = pos1 - pos2
    a = np.dot(dir1, dir1)
    b = np.dot(dir1, dir2)
    c = np.dot(dir2, dir2)
    d = np.dot(dir1, w0)
    e = np.dot(dir2, w0)

    denom = a * c - b * b
    if np.abs(denom) < 1e-6:
        # Parallel rays
        intersect = np.array([np.nan, np.nan, np.nan])
    else:
        s = (b * e - c * d) / denom
        t = (a * e - b * d) / denom
        p1_closest = pos1 + s * dir1
        p2_closest = pos2 + t * dir2
        intersect = (p1_closest + p2_closest) / 2

    records.append({
        'Drone_X': drone_x,
        'Drone_Y': drone_y,
        'Drone_Z': drone_z,
        'Anchor1_Azimuth': np.degrees(az1),
        'Anchor1_Elevation': np.degrees(el1),
        'Anchor1_RSSI': rssi1,
        'Anchor2_Azimuth': np.degrees(az2),
        'Anchor2_Elevation': np.degrees(el2),
        'Anchor2_RSSI': rssi2,
        'Intersection_X': intersect[0],
        'Intersection_Y': intersect[1],
        'Intersection_Z': intersect[2]
    })

# Final DataFrame
result_df = pd.DataFrame(records)

print(result_df)

# Save to CSV
result_df.to_csv(r"C:\Users\aryas\Desktop\Visualization\triangulated_results.csv", index=False)

print("✅ Table saved as triangulated_results.csv")
