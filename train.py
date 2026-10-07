


# train.py
import os
import cv2
import numpy as np
import pickle

DATA_DIR = "data"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Build dataset: each subfolder in data/ is a person
label_map = {}      # name -> numeric label
faces = []          # images (grayscale)
labels = []         # corresponding numeric labels

person_folders = [d for d in os.listdir(DATA_DIR)
                  if os.path.isdir(os.path.join(DATA_DIR, d))]
person_folders.sort()  # stable order

if not person_folders:
    raise RuntimeError("No person folders found in 'data/'. Run capture_faces.py first.")

for idx, person in enumerate(person_folders):
    label_map[person] = idx
    folder_path = os.path.join(DATA_DIR, person)

    for file in os.listdir(folder_path):
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        img_path = os.path.join(folder_path, file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        # Normalize input size
        img = cv2.resize(img, (200, 200))
        faces.append(img)
        labels.append(idx)

if len(faces) < 2 or len(set(labels)) < 1:
    raise RuntimeError("Not enough training data. Capture more images for at least one person.")

faces = np.array(faces, dtype=np.uint8)
labels = np.array(labels, dtype=np.int32)

print(f"Training on {len(faces)} images from {len(label_map)} person(s)...")

# Create and train LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create(
    radius=1, neighbors=8, grid_x=8, grid_y=8  # defaults are solid; tweak if needed
)
recognizer.train(faces, labels)

# Save model and label map
model_path = os.path.join(MODELS_DIR, "lbph_model.xml")
labels_path = os.path.join(MODELS_DIR, "labels.pkl")

recognizer.write(model_path)
with open(labels_path, "wb") as f:
    pickle.dump(label_map, f)

print(f"Saved model -> {model_path}")
print(f"Saved labels -> {labels_path}")
