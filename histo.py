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

    azimuth_real = (azimuth_real + 180) % 360
    if azimuth_real > 180:
        azimuth_real -= 360

    elevation_real = np.degrees(np.arctan2(dz, np.hypot(dx, dy)))

    real_azimuths.append(azimuth_real)
    real_elevations.append(elevation_real)

df['real_azimuth'] = real_azimuths
df['real_elevation'] = real_elevations

# Compute per-row error
df['azimuth_error'] = abs(df['real_azimuth'] - df['azimuth'])
df['elevation_error'] = abs(df['real_elevation'] - df['elevation'])

# Group by unique point
table = df.groupby(
    ['drone_x', 'drone_y', 'drone_z', 'peer_mac']
).agg(
    avg_real_azimuth=('real_azimuth', 'mean'),
    avg_experimental_azimuth=('azimuth', 'mean'),
    avg_real_elevation=('real_elevation', 'mean'),
    avg_experimental_elevation=('elevation', 'mean'),
    mean_azimuth_error=('azimuth_error', 'mean'),
    mean_elevation_error=('elevation_error', 'mean')
).reset_index()

# Save table
table_csv = "average_angles_and_errors.csv"
table.to_csv(table_csv, index=False)
print(f"✅ Saved table: {table_csv}")

# Find best, worst, and avg error points
def pick_points(col):
    best_idx = table[col].idxmin()
    worst_idx = table[col].idxmax()
    avg_val = table[col].mean()
    avg_idx = (table[col] - avg_val).abs().idxmin()
    return best_idx, avg_idx, worst_idx

az_best, az_avg, az_worst = pick_points('mean_azimuth_error')
el_best, el_avg, el_worst = pick_points('mean_elevation_error')

def print_point(name, row, col):
    print(f"📍 {name}: X={row['drone_x']}, Y={row['drone_y']}, Z={row['drone_z']}, MAC={row['peer_mac']}, {col}={row[col]:.2f}")

print("\n🔷 Azimuth Error Points:")
print_point("Best", table.loc[az_best], 'mean_azimuth_error')
print_point("Average", table.loc[az_avg], 'mean_azimuth_error')
print_point("Worst", table.loc[az_worst], 'mean_azimuth_error')

print("\n🔷 Elevation Error Points:")
print_point("Best", table.loc[el_best], 'mean_elevation_error')
print_point("Average", table.loc[el_avg], 'mean_elevation_error')
print_point("Worst", table.loc[el_worst], 'mean_elevation_error')

# Annotated histograms
def plot_hist(col, best_idx, avg_idx, worst_idx, title, xlabel):
    plt.figure(figsize=(10,6))
    plt.hist(table[col], bins=30, color='lightgray', edgecolor='k')
    for idx, color, label in zip([best_idx, avg_idx, worst_idx],
                                 ['g', 'orange', 'r'],
                                 ['Best', 'Average', 'Worst']):
        val = table.loc[idx, col]
        row = table.loc[idx]
        plt.axvline(val, color=color, linestyle='--', label=f"{label}: {val:.2f}\n({row['drone_x']},{row['drone_y']},{row['drone_z']},{row['peer_mac']})")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.show()

plot_hist('mean_azimuth_error', az_best, az_avg, az_worst,
          "Mean Azimuth Error per Point", "Azimuth Error (degrees)")

plot_hist('mean_elevation_error', el_best, el_avg, el_worst,
          "Mean Elevation Error per Point", "Elevation Error (degrees)")
