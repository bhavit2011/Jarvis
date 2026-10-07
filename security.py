import cv2
import pickle
import os
import time
import pyttsx3


# =========================================================
# SETTINGS
# =========================================================

PASSWORD = "python2022"   # <-- APNA PASSWORD YAHAN DALO

MODEL_PATH = "models/lbph_model.xml"
LABELS_PATH = "models/labels.pkl"
CASCADE_PATH = "haarcascade_frontalface_default.xml"

CAMERA_INDEX = 0

# LBPH: lower confidence = better match
CONFIDENCE_THRESHOLD = 70


# =========================================================
# TEXT TO SPEECH
# =========================================================

def speak(text):
    print("JARVIS:", text)

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 160)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")

        if voices:
            for voice in voices:
                voice_name = getattr(voice, "name", "").lower()

                if "english" in voice_name:
                    engine.setProperty("voice", voice.id)
                    break

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("TTS ERROR:", e)


# =========================================================
# CHECK REQUIRED FILES
# =========================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"\nFace model not found:\n{MODEL_PATH}"
    )

if not os.path.exists(LABELS_PATH):
    raise FileNotFoundError(
        f"\nLabels file not found:\n{LABELS_PATH}"
    )

if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(
        f"\nHaar Cascade file not found:\n{CASCADE_PATH}"
    )


# =========================================================
# LOAD LBPH FACE RECOGNIZER
# =========================================================

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.read(MODEL_PATH)


# =========================================================
# LOAD LABEL MAP
# =========================================================

with open(LABELS_PATH, "rb") as f:
    label_map = pickle.load(f)

# Example:
# label_map = {"Bhavit": 0}

reverse_labels = {
    value: key
    for key, value in label_map.items()
}


# =========================================================
# LOAD HAAR CASCADE
# =========================================================

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    raise RuntimeError(
        "\nHaar Cascade XML load nahi hui!"
    )


# =========================================================
# FACE SCANNING
# =========================================================

def scan_face():

    speak("Scanning face.")

    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        speak("Camera could not be accessed.")
        return False

    recognized = False
    recognized_name = "User"

    start_time = time.time()

    # Scan for maximum 10 seconds
    while time.time() - start_time < 10:

        ret, frame = cap.read()

        if not ret:
            print("Could not read camera frame.")
            break

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:

            face = gray[y:y+h, x:x+w]

            face = cv2.resize(
                face,
                (200, 200)
            )

            label, confidence = recognizer.predict(face)

            name = reverse_labels.get(
                label,
                "Unknown"
            )

            # ---------------------------------------------
            # FACE RECOGNIZED
            # ---------------------------------------------

            if confidence < CONFIDENCE_THRESHOLD:

                recognized = True
                recognized_name = name

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Welcome {name}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            # ---------------------------------------------
            # UNKNOWN FACE
            # ---------------------------------------------

            else:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Unknown",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

        # Top text
        cv2.putText(
            frame,
            "SCANNING FACE...",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "JARVIS SECURITY",
            frame
        )

        # ---------------------------------------------
        # RECOGNIZED -> STOP SCANNING
        # ---------------------------------------------

        if recognized:

            cv2.waitKey(500)
            break

        # Q = manually stop scan
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # =====================================================
    # CLOSE CAMERA
    # =====================================================

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    # =====================================================
    # FACE RESULT
    # =====================================================

    if recognized:

        print(f"Face recognized: {recognized_name}")

        # Camera is completely closed now
        speak("Access granted.")

        return True

    return False


# =========================================================
# PASSWORD LOGIN
# =========================================================

def password_login():

    # Camera is already OFF here

    speak(
        "Face not recognized. "
        "Please enter your password."
    )

    password = input(
        "Enter JARVIS password: "
    )

    return password == PASSWORD


# =========================================================
# RED ALERT
# =========================================================

def red_alert():

    print("\n==============================")
    print("       RED ALERT")
    print("==============================\n")

    while True:

        speak(
            "Red alert. "
            "Unauthorized access detected."
        )

        time.sleep(1)


# =========================================================
# SECURITY CHECK
# =========================================================

def security_check():

    # =====================================================
    # 1. TRY FACE RECOGNITION
    # =====================================================

    if scan_face():
        return True

    # =====================================================
    # 2. FACE FAILED -> PASSWORD
    # =====================================================

    if password_login():

        # CORRECT PASSWORD
        speak("Access granted.")

        return True

    # =====================================================
    # 3. WRONG PASSWORD -> RED ALERT
    # =====================================================

    speak(
        "Incorrect password. "
        "Red alert activated."
    )

    red_alert()

    return False


# =========================================================
# START TEST
# =========================================================

if __name__ == "__main__":

    access_granted = security_check()

    if access_granted:

        print("\n✅ JARVIS ACCESS GRANTED")
        print("Starting Jarvis...")

    else:

        print("\n❌ JARVIS ACCESS DENIED")
        