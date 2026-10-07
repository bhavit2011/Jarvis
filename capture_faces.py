# capture_faces.py
import cv2
import os
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

person_name = input("Enter person name : ").strip()
person_dir = os.path.join(DATA_DIR, person_name)
os.makedirs(person_dir, exist_ok=True)

# Try to open webcam
cap = cv2.VideoCapture(0)  # 0 = default webcam, change to 1 if you have multiple
if not cap.isOpened():
    raise RuntimeError(
        "❌ ERROR: Could not access webcam.\n"
        "👉 Close apps like Discord, Zoom, Meet, Teams, etc. and try again.\n"
        "👉 If it still fails, change cap = cv2.VideoCapture(0) to cap = cv2.VideoCapture(1)."
    )

# Use OpenCV's built-in Haar cascade (ships with cv2)
face_cascade = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)

print("Cascade empty:", face_cascade.empty())

print("\n--- Instructions ---")
print("Position your face in the box. Press 'c' to capture, 'q' to quit.")
print("Aim for 30–60 varied captures (angles/lighting/expressions).\n")

count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame grab failed. Webcam disconnected?")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                          minSize=(120, 120))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.putText(frame, f"Captures: {count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
    cv2.putText(frame, "Press 'c' to capture, 'q' to quit",
                (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Capture Faces", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        if len(faces) == 0:
            print("⚠️ No face detected — adjust lighting or move closer.")
        else:
            (x, y, w, h) = max(faces, key=lambda r: r[2] * r[3])
            face_crop = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_crop, (200, 200))
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            path = os.path.join(person_dir, f"{person_name}_{ts}.png")
            cv2.imwrite(path, face_resized)
            count += 1
            print(f"✅ Saved {path}")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
 
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("Cascade path:", cv2.data.haarcascades)
print("Cascade empty:", face_cascade.empty())