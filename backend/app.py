from flask import Flask, jsonify
from flask import request
from werkzeug.utils import secure_filename
import tempfile
from PIL import Image
import pytesseract
import os
import backend.config
from google import generativeai as genai


app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/check_key")
def check_key():
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return jsonify({
            "loaded" : True,
            "key_length" : len(key)
        })
    else:
        return jsonify({
            "loaded": False,
            "message":"Not found in .env file"
        })


    

@app.route("/summarize", methods=["POST"])
def summarize_text():
    """
    Takes raw text from OCR, sends it to Gemini, and returns structured summary info.
    """

    # Step 1: Get your Gemini API key from .env
    gemini_key = os.getenv("GEMINI_API_KEY")

    # Step 2: Get the text sent by the user
    data = request.get_json()
    raw_text = data.get("text", "")

    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    # Step 3: Make sure the API key exists
    if not gemini_key:
        return jsonify({"error": "API key not found"}), 500

    # Step 4: Configure Gemini
    genai.configure(api_key=gemini_key)

    # Step 5: Create a prompt that asks Gemini to summarize the syllabus text
    prompt = f"""
    You are an assistant that extracts key information from a syllabus.
    Summarize this text into JSON format with the following fields:
    - deadlines
    - grading_policy
    - attendance
    Text: {raw_text}
    """

    # Step 6: Run the Gemini model
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    # Step 7: Return the summarized text
    return jsonify({"summary": response.text}), 200



# Allowed images types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    # Check if the filename has a dot (.) in it
    if "." not in filename:
        return False  # No extension found, not allowed

    # Split the filename into two parts: name and extension
    name, extension = filename.rsplit(".", 1)

    # Make the extension lowercase (so JPG and jpg are treated the same)
    extension = extension.lower()

    # Check if the extension is in our allowed list (png, jpg, jpeg)
    if extension in ALLOWED_EXTENSIONS:
        return True
    else:
        return False
 
   
if __name__ == "__main__":
    app.run(host="127.0.0.1", port = 5000, debug = True)

