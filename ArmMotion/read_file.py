# from pathlib import Path
# import pandas as pd

# mot_file = Path(
#     r"C:\Users\fifty\Documents\ArmMotion\kinematics"
#     r"\ArmMotion_1-310_filt_butterworth_LSTM.mot"
# )

# with open(mot_file) as file:
#     for line_number, line in enumerate(file):
#         if line.strip().lower() == "endheader":
#             break

# angles = pd.read_csv(mot_file, sep=r"\s+", skiprows=line_number + 1)

# selected_columns = [
#     "time",
#     "arm_flex_r",     # shoulder flexion / extension
#     "arm_add_r",      # shoulder adduction / abduction
#     "elbow_flex_r",   # elbow flexion / extension
# ]

# arm_angles = angles[selected_columns].rename(columns={
#     "arm_flex_r": "shoulder_flexion",
#     "arm_add_r": "shoulder_abduction",
#     "elbow_flex_r": "elbow_flexion",
# })

# print(arm_angles.head())

# arm_angles.to_csv(
#     r"C:\Users\fifty\Documents\ArmMotion\arm_angles.csv",
#     index=False
# )

# print("\nSaved:arm_angles.csv")

from pathlib import Path
import pandas as pd

error_file = next(Path("kinematics").glob("*_ik_marker_errors.sto"))

with open(error_file) as file:
    for line_number, line in enumerate(file):
        if line.strip().lower() == "endheader":
            break

errors = pd.read_csv(error_file, sep=r"\s+", skiprows=line_number + 1)

error_columns = [c for c in errors.columns if c.lower() != "time"]

summary = pd.DataFrame({
    "mean_error_cm": errors[error_columns].mean() * 100,
    "max_error_cm": errors[error_columns].max() * 100,
}).sort_values("mean_error_cm", ascending=False)

print(summary)

