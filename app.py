import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_file
from utils.extract_text import extract_text
from utils.triage_prompt import triage_referral
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
DB_PATH = "triage.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS triage_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            decision TEXT,
            created_at TEXT
        )''')
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file:
            text = extract_text(uploaded_file)
            if text.strip():
                result = triage_referral(text)
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        "INSERT INTO triage_results (filename, decision, created_at) VALUES (?, ?, ?)",
                        (uploaded_file.filename, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    )
            else:
                result = "⚠️ Unable to extract text from the uploaded file."
    return render_template("index.html", result=result)

@app.route("/download")
def download():
    pdf_path = "triage_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 60, "Beacon NOUS Triage Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%d %B %Y, %H:%M')}")

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT filename, decision, created_at FROM triage_results ORDER BY id DESC LIMIT 1").fetchone()
    if row:
        filename, decision, created_at = row
        c.drawString(50, height - 110, f"Referral: {filename}")
        text_obj = c.beginText(50, height - 140)
        text_obj.setFont("Helvetica", 10)
        for line in decision.split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)
    else:
        c.drawString(50, height - 120, "No triage records found.")

    c.save()
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
