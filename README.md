# 🧾 SyllabusExplainer

## 🎥 Demo  
[▶️ Watch the 1-minute demo here](https://www.youtube.com/watch?v=SaBRyxjXSiM)

---

## 💡 Why Did I Create This?

I always felt like reading a syllabus is so boring and time-consuming.  
When I asked other students if they actually read theirs, most said no and that’s when the idea for this project came to me!  

---

## 🧠 What Is SyllabusExplainer?

**SyllabusExplainer** is a simple web app that helps students quickly understand their course syllabi.  

You can upload an image or PDF of your syllabus, and the app will **read it using OCR (Optical Character Recognition)** and **summarize the key parts** using **Google’s Gemini AI API**.  

It’s built to save time instead of reading through pages of text, you get a short, clear summary of grading, deadlines, and key topics in seconds.  
(I’m still working on improvements!)

---

## ⚙️ What It Does

- 🖼️ Reads text from syllabus images or PDFs  
- 💬 Summarizes key information in plain English  
- ⚙️ Uses a Flask backend to handle the processing  
- 🌐 Has a simple **React** frontend  

---

## 🔍 How It Works

1. Upload your syllabus file (`.jpg`, `.png`, or `.pdf`)  
2. The Flask backend uses **Tesseract OCR** to extract the text  
3. That text is sent to **Gemini AI**, which summarizes it  
4. The summary comes on the website  

---

## 🏗️ Built With

| Part | Technology |
|------|-------------|
| **Frontend** | React |
| **Backend** | Python (Flask) |
| **AI** | Gemini API |
| **OCR** | Tesseract |
| **Hosting (in progress)** | Render / Railway / Google Cloud |

---
## 🔍 Resources helped me achive this
- Watched YouTube tutorials to learn **React** and improve the frontend.  
- Used **AI tools** to understand parts of the Flask backend and crucial stuff needed for backend

---

## 🧩 How to Run It Locally

### Step 1: Clone the repo
```
git clone https://github.com/<your-username>/SyllabusExplainer.git
cd SyllabusExplainer/backend
```

### Step 2: Set up your environment
```
Copy code
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Add your Gemini API key
Create a file named .env inside the backend folder and add:
```
ini
Copy code
GEMINI_API_KEY=your_api_key_here
```

### Step 4: Run the Flask server
```
Copy code
python app.py
```

### Step 5: Run the frontend
```
Open the frontend folder in your browser or run it with your React development server.
Make sure your Flask backend is running first.
```


