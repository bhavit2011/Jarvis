# recognize.py
import cv2
import os
import pickle

MODELS_DIR = "models"
MODEL_FILE = os.path.join(MODELS_DIR, "lbph_model.xml")
LABELS_FILE = os.path.join(MODELS_DIR, "labels.pkl")

if not (os.path.exists(MODEL_FILE) and os.path.exists(LABELS_FILE)):
    raise RuntimeError("Model or labels not found. Run train.py first.")

# Load model + labels
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_FILE)
with open(LABELS_FILE, "rb") as f:
    label_map = pickle.load(f)

# Reverse map: id -> name
id_to_name = {v: k for k, v in label_map.items()}

face_cascade = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam.")

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                          minSize=(120, 120))

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_gray = cv2.resize(roi_gray, (200, 200))

        label_id, confidence = recognizer.predict(roi_gray)
        # Lower confidence value means better match for LBPH
        name = id_to_name.get(label_id, "Unknown")

        # Choose threshold: tweak ~60–90 depending on your data
        THRESHOLD = 50.0
        display_name = name if confidence < THRESHOLD else "Unknown"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        text = f"{display_name} ({confidence:.1f})"
        cv2.putText(frame, text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Face Recognition (LBPH)", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

