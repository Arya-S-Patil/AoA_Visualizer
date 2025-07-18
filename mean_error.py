import pandas as pd
import numpy as np

# Load triangulated results
df = pd.read_csv(r"C:\Users\aryas\Desktop\Visualization\triangulated_results.csv")

# Compute error for each row
df['Error'] = np.sqrt(
    (df['Drone_X'] - df['Intersection_X'])**2 +
    (df['Drone_Y'] - df['Intersection_Y'])**2 +
    (df['Drone_Z'] - df['Intersection_Z'])**2
)

# Group by unique position and take mean error
summary = df.groupby(['Drone_X', 'Drone_Y', 'Drone_Z'])['Error'].mean().reset_index()

summary.rename(columns={'Error': 'Mean_Error'}, inplace=True)

# Save
summary.to_csv(r"C:\Users\aryas\Desktop\Visualization\accuracy_by_position.csv", index=False)

print("✅ Saved: accuracy_by_position.csv")
print(summary.head())
