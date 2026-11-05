import numpy as np
import pandas as pd

INPUT_FILE = "arm_angles.csv"
OUTPUT_FILE = "arm_motion_ml_ready.csv"

# 8 frames at 30 Hz = about 0.267 s ahead
PREDICTION_FRAMES = 8

ANGLE_COLUMNS = [
    "shoulder_flexion",
    "shoulder_abduction",
    "elbow_flexion",
]

df = pd.read_csv(INPUT_FILE)

# Sort and verify time data
df = df.sort_values("time").reset_index(drop=True)

# Smooth each angle over 5 samples (~0.17 s)
for angle in ANGLE_COLUMNS:
    df[f"{angle}_smooth_deg"] = (
        df[angle]
        .rolling(window=5, center=True, min_periods=1)
        .mean()
    )

# Calculate angular velocity in deg/s
for angle in ANGLE_COLUMNS:
    df[f"{angle}_velocity_deg_s"] = np.gradient(
        df[f"{angle}_smooth_deg"],
        df["time"]
    )

# Create future joint-angle targets
for angle in ANGLE_COLUMNS:
    df[f"target_{angle}_deg"] = (
        df[f"{angle}_smooth_deg"]
        .shift(-PREDICTION_FRAMES)
    )

df["target_time_s"] = df["time"].shift(-PREDICTION_FRAMES)

# Last eight rows have no future target, so remove them
df = df.dropna().reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {len(df)} ML-ready samples to {OUTPUT_FILE}")
print("\nColumns available:")
print(df.columns.tolist())