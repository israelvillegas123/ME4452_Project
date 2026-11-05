from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Keep this script in the same folder as arm_motion_ml_ready.csv.
INPUT_FILE = "arm_motion_ml_ready.csv"
OUTPUT_DIR = Path("preliminary_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# Ignore the first 0.5 s in the two main plots because the signal has an
# initialization transient there. Keep all data in the raw-vs-smoothed plot.
START_TIME_S = 0.5

df = pd.read_csv(INPUT_FILE).sort_values("time").reset_index(drop=True)
df_plot = df[df["time"] >= START_TIME_S].copy()

angle_columns = [
    ("shoulder_flexion_smooth_deg", "Shoulder flexion"),
    ("shoulder_abduction_smooth_deg", "Shoulder abduction"),
    ("elbow_flexion_smooth_deg", "Elbow flexion"),
]

velocity_columns = [
    ("shoulder_flexion_velocity_deg_s", "Shoulder flexion"),
    ("shoulder_abduction_velocity_deg_s", "Shoulder abduction"),
    ("elbow_flexion_velocity_deg_s", "Elbow flexion"),
]

plt.style.use("seaborn-v0_8-whitegrid")

# Figure 1: smoothed joint angles.
fig, ax = plt.subplots(figsize=(8.2, 4.7), constrained_layout=True)
for column, label in angle_columns:
    ax.plot(df_plot["time"], df_plot[column], linewidth=2, label=label)

ax.set_title("Smoothed upper-arm joint angles after initial transient")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Joint angle (deg)")
ax.legend(frameon=True)
fig.savefig(OUTPUT_DIR / "joint_angles_vs_time.png", dpi=300)
plt.close(fig)

# Figure 2: estimated angular velocities.
fig, ax = plt.subplots(figsize=(8.2, 4.7), constrained_layout=True)
for column, label in velocity_columns:
    ax.plot(df_plot["time"], df_plot[column], linewidth=1.8, label=label)

ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Estimated angular velocities after initial transient")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Angular velocity (deg/s)")
ax.legend(frameon=True)
fig.savefig(OUTPUT_DIR / "angular_velocity_vs_time.png", dpi=300)
plt.close(fig)

# Figure 3: raw data versus smoothed data, used to justify preprocessing.
fig, axes = plt.subplots(
    3, 1, figsize=(8.2, 7.2), sharex=True, constrained_layout=True
)

for ax, (smooth_column, label) in zip(axes, angle_columns):
    raw_column = smooth_column.replace("_smooth_deg", "")

    ax.plot(
        df["time"], df[raw_column], color="gray", alpha=0.55,
        linewidth=1, label="Raw"
    )
    ax.plot(
        df["time"], df[smooth_column], color="#1f77b4",
        linewidth=2, label="Smoothed"
    )
    ax.set_title(label, loc="left", fontweight="bold")
    ax.set_ylabel("deg")

axes[0].legend(ncol=2, frameon=True)
axes[-1].set_xlabel("Time (s)")
fig.suptitle("Effect of moving-average smoothing on joint-angle signals")
fig.savefig(OUTPUT_DIR / "raw_vs_smoothed_angles.png", dpi=300)
plt.close(fig)

print("Created:")
for plot_path in sorted(OUTPUT_DIR.glob("*.png")):
    print(plot_path)
