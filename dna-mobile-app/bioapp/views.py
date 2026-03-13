import os
import json
import numpy as np
import pickle
import re
import random
import tensorflow as tf

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from tensorflow.keras.models import load_model
from PIL import Image as PILImage
from datetime import datetime

# ================= DETERMINISTIC MODE =================
os.environ['PYTHONHASHSEED'] = '42'
np.random.seed(42)
random.seed(42)
tf.random.set_seed(42)

try:
    tf.config.experimental.enable_op_determinism()
except:
    pass

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_BASE = os.path.join(BASE_DIR, "dataset")

USERS_FILE = os.path.join(BASE_DIR, "users.json")
REPORT_FILE = os.path.join(BASE_DIR, "reports.json")

# ================= LOAD MODELS =================
print("🔄 Loading ML & DL models...")

ml_model = pickle.load(open(os.path.join(BASE_DIR,"models/dna_nb_model.pkl"),"rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR,"models/vectorizer.pkl"),"rb"))
dl_model = load_model(os.path.join(BASE_DIR,"models/dl_model.h5"), compile=False)

# ================= LOAD DATASET CLASSES - YOUR MODEL CLASSES =================
print("🔍 Using YOUR trained model classes (Human, Rat, Worm)...")

# 🔥 YOUR SPECIFIC CLASSES - MATCHES YOUR .h5 TRAINING
DL_CLASSES = ['Human', 'Rat', 'Worm']

print("✅ YOUR Model classes:", DL_CLASSES)
print("📊 Model output shape:", dl_model.output_shape[-1])
print("🧬 DNA Classes:", ml_model.classes_)
print("📏 DL Input size: 128x128")

# ================= USERS & REPORTS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_reports():
    if not os.path.exists(REPORT_FILE):
        return []
    with open(REPORT_FILE) as f:
        return json.load(f)

def save_reports(data):
    with open(REPORT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_report(username, password, result, input_data):
    reports = load_reports()
    reports.append({
        "sno": len(reports) + 1,
        "name": username,
        "password": password,
        "input": input_data if input_data else "N/A",
        "result": result,
        "date": datetime.now().strftime("%d-%b-%Y %I:%M %p")
    })
    save_reports(reports)

# ================= ADMIN =================
ADMIN_USER = "Sai"
ADMIN_PASS = "2345"

# ================= VALIDATION =================
def validate_dna(dna_text):
    if not dna_text:
        return False, "DNA sequence "
    dna_text = dna_text.strip().upper()
    dna_clean = ''.join(c for c in dna_text if c in 'ATCG')

    if not re.fullmatch(r'^[ATCG]+$', dna_clean):
        return False, "Only A, T, C, G allowed"

    if len(dna_clean) < 15:
        return False, "DNA too short (min 15 chars)"

    return True, dna_clean

def validate_image_final(img_file):
    allowed_formats = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
    if not img_file.name.lower().endswith(tuple(allowed_formats)):
        return False, "Only JPG, PNG, TIF allowed"

    try:
        # Process image
        img = PILImage.open(img_file).convert("RGB").resize((128, 128), PILImage.Resampling.LANCZOS)
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # 🔥 YOUR TRAINED MODEL PREDICTION (Human, Rat, Worm)
        pred = dl_model.predict(img_array, verbose=0)[0]
        
        # Match prediction to YOUR 3 classes
        max_conf = float(np.max(pred))
        pred_idx = int(np.argmax(pred))
        pred_class = DL_CLASSES[pred_idx]

        sorted_probs = np.sort(pred)[::-1]
        second_max = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0
        
        if max_conf < 0.70:
            return False, f"❌ Low confidence:"
        
        confidence_gap = max_conf - second_max
        if confidence_gap < 0.20:
            return False, f"❌ Uncertain:"

        return True, (img, pred_class, f"{max_conf*100:.1f}%")

    except Exception as e:
        return False, f"❌ Image error:"

# ================= BASIC VIEWS =================
def welcome(request):
    return render(request, "welcome.html")

def register(request):
    if request.method == "POST":
        users = load_users()
        username = request.POST["username"].strip()

        if request.POST["password"] != request.POST["confirm_password"]:
            return render(request,"register.html",{"error":"Passwords do not match!"})

        if username in users:
            return render(request,"register.html",{"error":"User already exists!"})

        users[username] = {
            "email": request.POST["email"].strip(),
            "password": request.POST["password"],
            "role": "user"
        } 
        save_users(users)
        return redirect('/login/')
    return render(request,"register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        users = load_users()

        request.session.flush()

        if username == ADMIN_USER and password == ADMIN_PASS:
            request.session["logged_user"] = username
            request.session["is_admin"] = True
            return redirect("/admin-dashboard/?section=home")
        
        if username in users and users[username]["password"] == password:
            request.session["logged_user"] = username
            request.session["is_admin"] = False
            return redirect("/home/")

        return render(request,"login.html",{"error":"Invalid credentials!"})
    
    return render(request,"login.html")

def logout_view(request):
    request.session.flush()
    return redirect("/")

# ================= ADMIN FUNCTIONS =================
def admin_dashboard(request):
    if not request.session.get("logged_user") or not request.session.get("is_admin"):
        return redirect("/login/")

    users = load_users()
    reports = load_reports()

    user_list = []

    for uname, data in users.items():
        user_list.append({
            "sno": data.get("sno", 0),
            "username": uname,
            "email": data.get("email", ""),
            "password": data.get("password", ""),
            "role": data.get("role", "user")
        })
    current_section = request.GET.get("section", "home")      

    return render(request,"admin_dashboard.html",{
        "users": user_list,
        "reports": reports,
        "active_section": current_section,
        "total_users": len(users),
        "total_reports": len(reports),
        "user": request.session["logged_user"]
    })

def create_user(request):
    if not request.session.get('is_admin'):
        return redirect('/login/')

    if request.method == "POST":

        users = load_users()
        username = request.POST['username'].strip()

        if username not in users:

            new_sno = len(users) + 1

            users[username] = {
                "sno": new_sno,
                "email": request.POST['email'],
                "password": request.POST['password'],
                "role": "user"
            }

            save_users(users)

    section = request.GET.get("section", "home")
    return redirect(f'/admin-dashboard/?section={section}')

def edit_user(request):
    if not request.session.get('is_admin'):
        return redirect('/login/')

    if request.method == "POST":
        users = load_users()

        old_username = request.POST.get("old_username")
        new_username = request.POST.get("username").strip()
        email = request.POST.get("email")
        password = request.POST.get("password")

        if old_username in users:

            # If username changed
            if new_username != old_username:
                users[new_username] = users.pop(old_username)

            users[new_username]["email"] = email
            users[new_username]["password"] = password

            save_users(users)

    section = request.GET.get("section", "users")
    return redirect(f'/admin-dashboard/?section={section}')

def delete_user(request, username):
    if not request.session.get("logged_user") or not request.session.get("is_admin"):
        return redirect("/login/")

    users = load_users()
    current_admin = request.session.get("logged_user")
    
    # Admin self-delete block
    if username == current_admin:
        return redirect('/admin-dashboard/?section=users')

    # Delete user
    if username in users:
        del users[username]
        save_users(users)

    # Always redirect to users section
    return redirect('/admin-dashboard/?section=users')


def delete_report(request, sno):
    if not request.session.get('is_admin'):
        return redirect('/login/')
    
    try:
        sno_int = int(sno)
        reports = load_reports()
        reports = [r for r in reports if r["sno"] != sno_int]
        for i, r in enumerate(reports, start=1):
            r["sno"] = i
        save_reports(reports)
    except:
        pass
    
    section = request.GET.get("section", "reports")
    return redirect(f'/admin-dashboard/?section={section}')

# ================= HOME =================
def home(request):
    if not request.session.get("logged_user"):
        return redirect("/login/")
    
    if request.session.get("is_admin"):
        return redirect("/admin-dashboard/")
    
    reports = load_reports()
    
    return render(request,"home.html",{
        "user": request.session["logged_user"],
        "reports": reports,
        "total_reports": len(reports)
    })

# ================= PREDICT =================
# ================= PREDICT =================
def predict(request):
    if not request.session.get("logged_user"):
        return redirect("/login/")

    if request.method == "POST":
        username = request.session["logged_user"]
        users = load_users()
        password = users.get(username, {}).get("password", "")

        dna_text = request.POST.get("dna_text", "").strip()
        img_file = request.FILES.get("image")

        # ✅ CHECK IF FROM ADMIN DASHBOARD
        from_admin = request.session.get("is_admin", False)

        if dna_text:
            is_valid, result = validate_dna(dna_text)
            if not is_valid:
                return render(request,"result.html",{"error": result, "from_admin": from_admin})

            vect = vectorizer.transform([result])
            ml_proba = ml_model.predict_proba(vect.toarray())[0]
            pred_class = ml_model.classes_[np.argmax(ml_proba)]
            confidence = float(np.max(ml_proba))

            add_report(username, password, pred_class, result[:100]+"...")

            return render(request,"result.html",{
                "ml_result": pred_class,
                "ml_confidence": f"{confidence*100:.1f}%",
                "top_probs": [{"class": ml_model.classes_[i], "prob": f"{p*100:.1f}%"}
                             for i, p in enumerate(ml_proba[:3])],
                "from_admin": from_admin  # ✅ PASS TO TEMPLATE
            })

        elif img_file:
            is_valid, result = validate_image_final(img_file)
            if not is_valid:
                return render(request,"result.html",{"error": str(result), "from_admin": from_admin})

            img, predicted_class, confidence = result
            add_report(username, password, predicted_class, img_file.name)

            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            dl_proba = dl_model.predict(img_array, verbose=0)[0]

            return render(request,"result.html",{
                "dl_result": predicted_class,
                "confidence": confidence,
                "top_probs": [{"class": DL_CLASSES[i], "prob": f"{p*100:.1f}%"}
                             for i, p in enumerate(dl_proba[:3])],
                "from_admin": from_admin  # ✅ PASS TO TEMPLATE
            })

        return render(request,"result.html",{"error": "DNA or Image required", "from_admin": from_admin})

    # GET request - Admin goes to predict section
    if request.session.get("is_admin"):
        return redirect("/admin-dashboard/?section=home")
    return redirect("/home/")

# ================= API =================
@csrf_exempt
def api_predict(request):
    if request.method == "POST":
        dna_text = request.POST.get("dna_text", "").strip()
        img_file = request.FILES.get("image")

        if dna_text:
            is_valid, result = validate_dna(dna_text)
            if not is_valid:
                return JsonResponse({"error": result}, status=400)

            vect = vectorizer.transform([result])
            ml_proba = ml_model.predict_proba(vect.toarray())[0]

            return JsonResponse({
                "species": ml_model.classes_[np.argmax(ml_proba)],
                "confidence": f"{np.max(ml_proba)*100:.1f}%"
            })

        elif img_file:
            is_valid, result = validate_image_final(img_file)
            if not is_valid:
                return JsonResponse({"error": str(result)}, status=400)

            img, predicted_class, confidence = result

            return JsonResponse({
                "species": predicted_class,
                "confidence": confidence
            })

    return JsonResponse({"error": "POST dna_text or image required"}, status=400)
