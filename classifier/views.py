from django.shortcuts import render
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from django.core.files.storage import FileSystemStorage
import pickle
import re

# DL model
dl_model = load_model("models/dl_model.h5")

dl_classes = [
    "Malaria Infected",
    "Malaria Normal",
    "Normal Worm",
    "Mutant Worm",
    "Rat Cells"
]

# ML model
ml_model = pickle.load(open("models/dna_nb_model.pkl", "rb"))
vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))

def home(request):
    return render(request, "home.html")

def predict(request):

    dl_result = None
    ml_result = None
    error = None

    # IMAGE PREDICTION
    if request.FILES.get('image'):
        file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        path = fs.path(filename)

        img = cv2.imread(path)
        img = cv2.resize(img, (64,64))
        img = img / 255.0
        img = np.reshape(img, (1,64,64,3))

        prediction = dl_model.predict(img)
        dl_result = dl_classes[np.argmax(prediction)]

    # DNA PREDICTION WITH VALIDATION
    if request.POST.get('dna'):
        dna_text = request.POST.get('dna')

        # clean input
        dna_text = dna_text.upper().replace(" ", "").replace("\n", "")

        # check valid letters
        if not re.fullmatch(r'[ATGC]+', dna_text):
            error = "DNA must contain only A, T, G, C letters."

        # length validation
        elif len(dna_text) < 20:
            error = "DNA sequence too short (min 20 letters)."

        elif len(dna_text) > 1000:
            error = "DNA sequence too long (max 1000 letters)."

        else:
            vec = vectorizer.transform([dna_text])
            ml_result = ml_model.predict(vec)[0]

    return render(request, "result.html", {
        "dl": dl_result,
        "ml": ml_result,
        "error": error
    })
