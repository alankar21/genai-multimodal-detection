from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
from PIL import Image
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOAD MODELS ----------------

image_model = joblib.load("models/image_model.pkl")
text_model = joblib.load("models/text_model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")


# ---------------- FEATURE EXTRACTION ----------------

def extract_dummy_features(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    img = img.resize((128, 128))

    arr = np.array(img)

    # Convert to grayscale
    gray = np.mean(arr, axis=2)

    features = []

    # ---- Basic Intensity Statistics ----
    features.append(np.mean(gray))
    features.append(np.std(gray))
    features.append(np.min(gray))
    features.append(np.max(gray))

    # ---- Color Channel Statistics ----
    for i in range(3):  # R, G, B
        channel = arr[:, :, i]
        features.append(np.mean(channel))
        features.append(np.std(channel))

    # ---- Edge Strength Approximation ----
    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    edge_strength = np.mean(np.abs(gx)) + np.mean(np.abs(gy))
    features.append(edge_strength)

    # ---- Texture Variation ----
    features.append(np.var(gray))

    # Pad to 100 features (model expects 100 features)
    while len(features) < 100:
        features.append(0)

    return np.array(features)


# ---------------- ROUTES ----------------

@app.get("/")
def home():
    return {"message": "GenAI Multimodal Detection API Running"}


@app.post("/predict")
async def predict(image: UploadFile = File(None), text: str = Form(None)):

    result = {
        "image_probability": None,
        "text_probability": None,
        "risk_level": None,
        "explanation": ""
    }

    # ---------- IMAGE PREDICTION ----------
    if image:
        contents = await image.read()
        features = extract_dummy_features(contents)
        prediction = image_model.predict_proba([features])[0][1]
        result["image_probability"] = float(prediction)

    # ---------- TEXT PREDICTION ----------
    if text:
        text_features = vectorizer.transform([text])
        text_prediction = text_model.predict_proba(text_features)[0][1]
        result["text_probability"] = float(text_prediction)

    # ---------- COMBINED RISK LOGIC ----------
    image_score = result["image_probability"] or 0
    text_score = result["text_probability"] or 0

    final_score = max(image_score, text_score)

    if final_score > 0.7:
        result["risk_level"] = "High"
    elif final_score > 0.4:
        result["risk_level"] = "Medium"
    else:
        result["risk_level"] = "Low"

    result["explanation"] = "Multimodal prediction using statistical, color, and texture-based features."

    return result
