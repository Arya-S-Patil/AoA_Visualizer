import pandas as pd
import matplotlib.pyplot as plt

# Read the grouped table
table = pd.read_csv(r"C:\Users\aryas\Desktop\Visualization\average_angles_and_errors.csv")

# Previously identified points
def pick_points(col):
    best_idx = table[col].idxmin()
    worst_idx = table[col].idxmax()
    avg_val = table[col].mean()
    avg_idx = (table[col] - avg_val).abs().idxmin()
    return best_idx, avg_idx, worst_idx

az_best, az_avg, az_worst = pick_points('mean_azimuth_error')
el_best, el_avg, el_worst = pick_points('mean_elevation_error')

# List of (label, index, real, experimental, type)
points = [
    ("Azimuth Best", az_best, 'avg_real_azimuth', 'avg_experimental_azimuth', 'Azimuth'),
    ("Azimuth Average", az_avg, 'avg_real_azimuth', 'avg_experimental_azimuth', 'Azimuth'),
    ("Azimuth Worst", az_worst, 'avg_real_azimuth', 'avg_experimental_azimuth', 'Azimuth'),
    ("Elevation Best", el_best, 'avg_real_elevation', 'avg_experimental_elevation', 'Elevation'),
    ("Elevation Average", el_avg, 'avg_real_elevation', 'avg_experimental_elevation', 'Elevation'),
    ("Elevation Worst", el_worst, 'avg_real_elevation', 'avg_experimental_elevation', 'Elevation'),
]

for label, idx, real_col, exp_col, typ in points:
    row = table.loc[idx]
    real_val = row[real_col]
    exp_val = row[exp_col]
    coords = f"({row['drone_x']:.1f}, {row['drone_y']:.1f}, {row['drone_z']:.1f})"
    mac = row['peer_mac']
    
    plt.figure(figsize=(5,4))
    plt.bar(['Real', 'Experimental'], [real_val, exp_val], color=['skyblue', 'salmon'])
    plt.ylabel(f"{typ} (degrees)")
    plt.title(f"{label}\nCoords: {coords} | MAC: {mac}")
    plt.tight_layout()
    plt.show()
