import pandas as pd
import numpy as np

# 📄 Load raw experimental data
df = pd.read_csv(r"C:\Users\aryas\Desktop\Visualization\Experiment1(50).csv", skiprows=1, low_memory=False)
df.columns = df.columns.str.strip().str.lower()

mac1 = '20BA36977463'
mac2 = '20BA369AFC6B'
anchor_positions = {
    mac1: np.array([0, 0, 0]),
    mac2: np.array([3, 0, 0])
}

df1 = df[df['peer_mac'] == mac1].copy().reset_index(drop=True)
df2 = df[df['peer_mac'] == mac2].copy().reset_index(drop=True)
df1['time_index'] = df1.index
df2['time_index'] = df2.index

merged = pd.merge_asof(
    df1.sort_values('time_index'),
    df2.sort_values('time_index'),
    on='time_index',
    direction='nearest',
    suffixes=('_1', '_2')
)

def triangulate(row, convention):
    fwd_axis, clockwise = convention
    drone_pos = np.array([row['drone_x_1'], row['drone_y_1'], row['drone_z_1']])

    pos1 = anchor_positions[mac1]
    pos2 = anchor_positions[mac2]

    # Anchor 1
    az1 = row['azimuth_1']
    el1 = row['elevation_1']
    # Anchor 2
    az2 = row['azimuth_2']
    el2 = row['elevation_2']

    def az_el_to_vec(az, el, fwd_axis, clockwise):
        az = np.radians(az)
        el = np.radians(el)

        if fwd_axis == 'Y':
            x = np.cos(el) * np.sin(az)
            y = np.cos(el) * np.cos(az)
        elif fwd_axis == 'X':
            x = np.cos(el) * np.cos(az)
            y = np.cos(el) * np.sin(az)

        if not clockwise:
            x = -x

        z = np.sin(el)
        return np.array([x, y, z])

    dir1 = az_el_to_vec(az1, el1, fwd_axis, clockwise)
    dir2 = az_el_to_vec(az2, el2, fwd_axis, clockwise)

    w0 = pos1 - pos2
    a = np.dot(dir1, dir1)
    b = np.dot(dir1, dir2)
    c = np.dot(dir2, dir2)
    d = np.dot(dir1, w0)
    e = np.dot(dir2, w0)
    denom = a*c - b*b

    if np.abs(denom) < 1e-6:
        return np.nan, np.nan, np.nan

    s = (b*e - c*d) / denom
    t = (a*e - b*d) / denom

    p1_closest = pos1 + s*dir1
    p2_closest = pos2 + t*dir2
    intersect = (p1_closest + p2_closest) / 2
    return intersect

conventions = [
    ('Y', True),
    ('Y', False),
    ('X', True),
    ('X', False)
]

results = []
for convention in conventions:
    errors = []
    for idx, row in merged.iterrows():
        intersect = triangulate(row, convention)
        drone_pos = np.array([row['drone_x_1'], row['drone_y_1'], row['drone_z_1']])
        if np.any(np.isnan(intersect)):
            continue
        err = np.linalg.norm(drone_pos - intersect)
        errors.append(err)
    avg_err = np.mean(errors)
    results.append((convention, avg_err))

# Sort and print best convention
results.sort(key=lambda x: x[1])
print("\n🔷 Convention testing results:")
for conv, err in results:
    fwd, cw = conv
    print(f"Forward={fwd}, Clockwise={cw} => Mean Error: {err:.3f} m")

best_conv = results[0][0]
print(f"\n✅ Best convention: Forward={best_conv[0]}, Clockwise={best_conv[1]}")

