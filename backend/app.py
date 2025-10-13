from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image
import pytesseract
import os
import re

# For PDF handling
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text as get_pdf_text

# For AI summarization  
from google import generativeai as genai
import json

# Load environment variables (API keys)
try:
    import backend.config
except:
    pass


# ============================================
# STEP 1: CREATE THE FLASK APP
# ============================================

app = Flask(__name__)

#  file uploads to 10MB (10 * 1024 * 1024 bytes)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Allow React app to talk to this Flask app
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})


# ============================================
# STEP 2: HELPER FUNCTIONS
# ============================================

def is_valid_file(filename):
    """
    Check if the uploaded file is a PDF, PNG, JPG, or JPEG
    """
    allowed_types = ["pdf", "png", "jpg", "jpeg"]
    
    if "." not in filename:
        return False
    
    # Get the file extension (e.g., "pdf" from "syllabus.pdf")
    file_extension = filename.split(".")[-1].lower()
    
    return file_extension in allowed_types


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    First tries to get native text, then falls back to OCR if needed
    """
    try:
        # Try to extract text directly (works for most PDFs)
        text = get_pdf_text(pdf_path) or ""
        
        # If we got enough text, return it
        if len(text.strip()) > 50:
            return text
    except:
        pass
    
    # If direct extraction didn't work, use OCR (slower but works on scanned PDFs)
    try:
        # Convert PDF pages to images
        pages = convert_from_path(pdf_path)
        
        # OCR each page and combine the text
        all_text = ""
        for page in pages:
            page_text = pytesseract.image_to_string(page)
            all_text += page_text + "\n"
        
        return all_text
    except:
        return ""


def find_course_info(text):
    """
    Find course code and name (e.g., "CS 101: Introduction to Computer Science")
    """
    pattern = r"^[A-Z]{2,4}\s?\d{2,3}[^:\n]*:\s*.+"
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(0).strip() if match else ""


def find_term(text):
    """
    Find the term/semester (e.g., "Fall 2024")
    """
    pattern = r"\b(Fall|Spring|Summer)\s+\d{4}\b"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0).strip() if match else ""


def find_instructor(text):
    """
    Find instructor name (e.g., "Professor John Smith")
    """
    pattern = r"(Professor|Prof\.?|Instructor)\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else ""


def find_email(text):
    """
    Find email address
    """
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else ""


def find_grading_breakdown(text):
    """
    Find grading components and their percentages
    Example: "Homework 30%" or "Final Exam: 40%"
    """
    grading = []
    
    # Look for lines with percentages
    for line in text.split("\n"):
        # Pattern: something followed by a number and %
        match = re.search(r"(.+?)\s+(\d{1,3})\s?%", line)
        
        if match:
            component_name = match.group(1).strip(" :-•*·")
            percentage = int(match.group(2))
            
            # Only include valid percentages (1-100%)
            if 0 < percentage <= 100:
                grading.append({
                    "component": component_name,
                    "weight_percent": percentage
                })
    
    # Remove duplicates and limit to first 12 items
    seen = set()
    unique_grading = []
    for item in grading:
        key = (item["component"].lower(), item["weight_percent"])
        if key not in seen:
            seen.add(key)
            unique_grading.append(item)
    
    return unique_grading[:12]


def find_important_dates(text):
    """
    Find dates mentioned in the syllabus
    """
    dates = []
    
    # Look for date patterns like "Jan 15" or "1/15/2024"
    for line in text.split("\n"):
        # Check if line contains a date
        if re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", line, re.IGNORECASE):
            dates.append(line.strip())
        elif re.search(r"\d{1,2}/\d{1,2}", line):
            dates.append(line.strip())
    
    # Return first 15 dates
    return dates[:15]


def create_simple_summary(text):
    """
    Create a summary using simple pattern matching
    This is the fallback if AI is not available
    """
    summary = {
        "course": find_course_info(text),
        "term": find_term(text),
        "meeting_time": "",
        "room": "",
        "instructor": find_instructor(text),
        "email": find_email(text),
        "office": "",
        "office_hours": "",
        "grading_weights": find_grading_breakdown(text),
        "attendance_policy": "",
        "important_dates": find_important_dates(text)
    }
    
    return summary


def create_ai_summary(text):
    """
    Use Google's Gemini AI to create a smarter summary
    """
    # Get API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return None  # No API key, can't use AI
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create a prompt for the AI
        prompt = f"""
        Extract key information from this college syllabus.
        Return ONLY valid JSON with these fields:
        - course (course code and name)
        - term (semester and year)
        - meeting_time (class schedule)
        - room (classroom location)
        - instructor (professor name)
        - email (contact email)
        - office (office location)
        - office_hours (when students can visit)
        - grading_weights (array of objects with component and weight_percent)
        - attendance_policy (attendance rules)
        - important_dates (array of important dates)
        
        Syllabus text:
        {text[:5000]}
        """
        
        # Ask AI to process the text
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Try to parse the AI's response as JSON
        result = json.loads(response.text)
        return result
        
    except Exception as e:
        print(f"AI summarization failed: {e}")
        return None  # AI failed, we'll use simple summary instead


# ============================================
# STEP 3: API ENDPOINTS (ROUTES)
# ============================================

@app.route("/")
def home():
    """
    Welcome page - shows available API endpoints
    """
    return jsonify({
        "message": "Welcome to Syllabus Explainer API!",
        "endpoints": {
            "/health": "Check if server is running",
            "/extract": "Upload a file to extract text",
            "/summarize": "Summarize syllabus text"
        }
    })


@app.route("/health")
def health_check():
    """
    Simple endpoint to check if the server is running
    """
    return jsonify({"status": "ok", "message": "Server is running!"})


@app.route("/check_key")
def check_api_key():
    """
    Check if Gemini API key is loaded
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        return jsonify({
            "loaded": True,
            "key_length": len(api_key),
            "message": "API key is loaded!"
        })
    else:
        return jsonify({
            "loaded": False,
            "message": "No API key found. Using basic extraction only."
        })


@app.route("/extract", methods=["POST"])
def extract_text_from_file():
    """
    Extract text from an uploaded PDF or image file
    """
    # Check if a file was uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    uploaded_file = request.files["file"]
    
    # Check if filename is empty
    if uploaded_file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Check if file type is allowed
    if not is_valid_file(uploaded_file.filename):
        return jsonify({"error": "Only PDF, PNG, JPG, and JPEG files are allowed"}), 400
    
    # Create uploads folder if it doesn't exist
    upload_folder = "backend/uploads"
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save the uploaded file temporarily
    filename = uploaded_file.filename
    file_path = os.path.join(upload_folder, filename)
    uploaded_file.save(file_path)
    
    extracted_text = ""
    
    try:
        # Get file extension
        file_extension = filename.split(".")[-1].lower()
        
        if file_extension in ["png", "jpg", "jpeg"]:
            # Extract text from image using OCR
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
            
        elif file_extension == "pdf":
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(file_path)
        
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    
    finally:
        # Delete the temporary file
        try:
            os.remove(file_path)
        except:
            pass
    
    # Return the extracted text
    return jsonify({
        "filename": filename,
        "characters_found": len(extracted_text),
        "text": extracted_text
    }), 200


@app.route("/summarize", methods=["POST"])
def summarize_syllabus():
    """
    Summarize the syllabus text and extract key information
    """
    # Get the text from the request
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Check what mode to use (auto, local, or gemini)
    mode = request.args.get("mode", "auto").lower()
    
    # Mode 1: Force local/simple summarization only
    if mode == "local":
        summary = create_simple_summary(text)
        return jsonify({"summary": summary}), 200
    
    # Mode 2: Try AI first, then fallback to simple (default)
    if mode == "auto":
        # Try AI summarization
        ai_summary = create_ai_summary(text)
        
        if ai_summary:
            return jsonify({"summary": ai_summary}), 200
        else:
            # AI failed, use simple summarization
            summary = create_simple_summary(text)
            return jsonify({"summary": summary}), 200
    
    # Mode 3: Force AI only (will fail if no API key)
    if mode == "gemini":
        ai_summary = create_ai_summary(text)
        
        if ai_summary:
            return jsonify({"summary": ai_summary}), 200
        else:
            return jsonify({"error": "AI summarization failed. Check your API key."}), 500
    
    # Default fallback
    summary = create_simple_summary(text)
    return jsonify({"summary": summary}), 200


# ============================================
# STEP 4: RUN THE SERVER
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Syllabus Explainer Server...")
    print("=" * 50)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("📚 Upload a syllabus to get started!")
    print("=" * 50)
    
    # Start the Flask server
    app.run(
        host="127.0.0.1",  # Run on localhost
        port=5000,          # Run on port 5000
        debug=True          # Show helpful error messages
    )