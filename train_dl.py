import os, cv2, numpy as np
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

BASE = r"C:\Users\dell\Desktop\SaiGanesh\Main Project\app7\dataset"

img_size = 64
data, labels = [], []

label_map = {}
label_id = 0

print("\n🔍 Scanning dataset folders...\n")

for root, dirs, files in os.walk(BASE):
    if len(files) > 0:
        print("Loading:", root)

        label_map[label_id] = os.path.basename(root)

        for f in files:
            try:
                img_path = os.path.join(root, f)
                img = cv2.imread(img_path)

                if img is None:
                    continue

                img = cv2.resize(img, (img_size, img_size))
                data.append(img)
                labels.append(label_id)
            except:
                pass

        label_id += 1

print("\nTotal classes found:", len(label_map))
print("Total images loaded:", len(data))
print("Class map:", label_map)

data = np.array(data) / 255.0
labels = to_categorical(labels)

model = Sequential([
    Conv2D(32,(3,3),activation='relu',input_shape=(64,64,3)),
    MaxPooling2D(2,2),
    Conv2D(64,(3,3),activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128,activation='relu'),
    Dense(len(label_map),activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.fit(data, labels, epochs=10, batch_size=32)

os.makedirs("models", exist_ok=True)
model.save("models/dl_model.h5")

print("\n✅ DL Training Complete")
