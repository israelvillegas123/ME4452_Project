# So far the code takes 2 videos that are synced up and splits into frames.
# We need 2 videos because we are tracking motion in different planes.
# These frames are then given to mediapipe. Mediapipe places landmarks on the 
# shoulder, elbow, and wrist. With these landmarks we need to calculate the 
# arm angles.
import mediapipe as mp # For arm landmarks. This tracks the arm.
import cv2 # For video processing.
import os # For file stuff.
import urllib.request # For downloading the model.

# Open the video files and selects the output folders
vid1 = cv2.VideoCapture("Webcam.mp4")
vid2 = cv2.VideoCapture("Phone.mp4")

output1 = "webcam_frames"
output2 = "phone_frames"

os.makedirs(output1, exist_ok=True)
os.makedirs(output2, exist_ok=True)
count1 = 0
count2 = 0

# Reads the frame rates of the videos
fps1 = vid1.get(cv2.CAP_PROP_FPS)
fps2 = vid2.get(cv2.CAP_PROP_FPS)

# Download the model if it doesn't exist
model_path = "pose_landmarker_lite.task"
model_url = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/"
    "pose_landmarker_lite.task"
)

# Define the joints of interest
joints = {
    "shoulder": 12,
    "elbow": 14,
    "wrist": 16,
}

if not os.path.exists(model_path):
        urllib.request.urlretrieve(model_url, model_path)

# Options for the pose landmarker
options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Initialize the pose landmarkers
landmarker1 = mp.tasks.vision.PoseLandmarker.create_from_options(options)
landmarker2 = mp.tasks.vision.PoseLandmarker.create_from_options(options)

# Store x, y, z coordinates, visibility and timestamp for each joint
webcam_landmarks = {joint: [] for joint in joints}
phone_landmarks = {joint: [] for joint in joints}

# Loop that saves each frame into the output folders
while True:
    ok1, frame1 = vid1.read()
    ok2, frame2 = vid2.read()
    if not ok1 and not ok2:
        vid1.release()
        vid2.release()
        break
    if ok1:
        cv2.imwrite(os.path.join(output1, f"frame_{count1:04d}.jpg"), frame1)
        count1 += 1
    if ok2:
        cv2.imwrite(os.path.join(output2, f"frame_{count2:04d}.jpg"), frame2)
        count2 += 1

# Loop that processes each frame with Mediapipe
for i in range(count1):
    img_path = os.path.join(output1, f"frame_{i:04d}.jpg")
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)

    time1 = int(i * 1000 / fps1 )
    results1 = landmarker1.detect_for_video(mp_image, time1)

    if results1.pose_landmarks:
        for joint, number in joints.items():
            landmark = results1.pose_landmarks[0][number]
            webcam_landmarks[joint].append(((landmark.x, landmark.y, landmark.z, landmark.visibility), time1))

# Process frames from the second video
for i in range(count2):
    img_path = os.path.join(output2, f"frame_{i:04d}.jpg")
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)

    time2 = int(i * 1000 / fps2 )
    results2 = landmarker2.detect_for_video(mp_image, time2)

    if results2.pose_landmarks:
        for joint, number in joints.items():
            landmark = results2.pose_landmarks[0][number]
            phone_landmarks[joint].append(((landmark.x, landmark.y, landmark.z, landmark.visibility), time2))

landmarker1.close()
landmarker2.close()

# Print the number of detections for each joint
print("Webcam shoulder detections:", len(webcam_landmarks["shoulder"]))
print("Phone shoulder detections:", len(phone_landmarks["shoulder"]))
print("Webcam elbow detections:", len(webcam_landmarks["elbow"]))
print("Phone elbow detections:", len(phone_landmarks["elbow"]))
print("Webcam wrist detections:", len(webcam_landmarks["wrist"]))
print("Phone wrist detections:", len(phone_landmarks["wrist"]))

# Next steps are to clean up the data, make sure that the video are synched up properly,
# and convert the landmark data into joint angles. After that the data is ready for
# machine learning models.