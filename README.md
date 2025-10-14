# 🧾 SyllabusExplainer


<!-- In README.md -->
<h2>🎥 Demo</h2>
[▶️ Watch the 1-minute demo here](https://www.youtube.com/watch?v=SaBRyxjXSiM)




# Why did I create this?

- I always felt like reading syllabus is so boring and time consuming. I asked other people whether they read their syllabi or not, they said no. This is then when I thought about making this website!
---

SyllabusExplainer is a simple web app that helps students quickly understand their course syllabi.  
You can upload an image or PDF of your syllabus, and the app will **read it using OCR (Optical Character Recognition)** and **summarize the important parts** using Google’s **Gemini AI API**.

It’s built to save students time, instead of reading through pages of text, you get a short, clear summary of grading, deadlines, and key topics in seconds.(I am working on improvements)

---

##  What It Does

- 🖼️ Reads text from syllabus images or PDFs  
- 💬 Summarizes key information in plain English  
- ⚙️ Uses a Flask backend to handle the processing  
- 🌐 Simple and clean Reactfrontend  


---

## How It Works

1. Upload syllabus file (.jpg, .png, or .pdf)  
2. The Flask backend uses **Tesseract OCR** to extract the text  
3. That text is sent to **Gemini AI**, which summarizes it  
4. The summary appears instantly on the website  

---

## Built With

| Part | Technology |
|------|-------------|
| **Frontend** | React |
| **Backend** | Python (Flask) |
| **AI** | Gemini API |
| **OCR** | Tesseract |
| **Hosting (working on this)** | Render / Railway / Google Cloud |

---

---

## ⚙️ How to Run It Locally

### Step 1: Clone the repo
```bash
git clone https://github.com/<your-username>/SyllabusExplainer.git
cd SyllabusExplainer/backend

Step 2: Set up your environment
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Step 3: Add your Gemini API key

Create a file named .env inside the backend folder and add:

GEMINI_API_KEY=your_api_key_here

Step 4: Run the Flask server
python app.py

Step 5: Open the frontend

Go to frontend and open it in your browser.
Make sure the backend is running first.

Need help, Go over to the video and look for the commands! I hope you enjoy.

