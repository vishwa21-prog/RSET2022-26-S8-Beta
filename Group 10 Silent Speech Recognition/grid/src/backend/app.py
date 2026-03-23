import os
from flask import Flask, request, jsonify
from model_loader import load_model, infer_video
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

model, tokenizer = load_model()

@app.route("/predict", methods=["POST"])
def predict():
    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    file = request.files["video"]
    path = "uploaded_video.mp4"
    file.save(path)

    prediction = infer_video(path, model, tokenizer, beam_width=15)

    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port,)