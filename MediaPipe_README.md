## MediaPipe Data-Processing Workflow

### 1. Collect video
Record an upper-arm motion trial at approximately 30 frames/s. Ensure the
shoulder, elbow, and wrist remain visible throughout the recording.

### 2. Extract pose landmarks
Place the following in one folder:

- `Webcam.mp4` or another motion video
- `pose_landmarker_lite.task`
- `collect_joint_csv.py`

Create and activate a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install mediapipe opencv-python numpy pandas matplotlib

## 3. Run Landmark-extraction script (this produces raw landmark and joint-angle CSV files) 
python collect_joint_csv.py

## 4. Prepare model inputs
After collecting joint angles and collecting in arm_angles.csv, run

python prepare_ml_data.py

This smooths joint-angles, calculates angular velocities, and predicts angles 0.267s ahead.

## 5. Generate prelim plots
Run:
python make_preliminary_plots.py

This saved joint-angle, angular-velocity, and raw-vs-smoothed plots in a preliminary_figures folder.
The following otput files are then created:
- arm_angles.csv: recorded joint-angle data
- arm_motion_ml_ready.csv: ML-ready angles, velocities, and future angles
