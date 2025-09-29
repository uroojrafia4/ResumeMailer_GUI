# Mini-ATS — Resume Parser & Email Sender

A simple GUI tool for parsing resumes into a CSV and sending personalized emails.  
Designed for a friend or personal use — drop resumes in a folder, parse them, and email applicants.

---

## Features
- Parse resumes (PDF, DOCX, images) from `./resumes` folder.
- Generate `applicants.csv` with name, email, job title, and job link.
- Send HTML + plain emails with an optional inline logo.
- Simple GUI with live logging.
- **Email Automation:** Sends personalized emails to applicants for a single job title and job link per run. To send emails for another job, simply update the job details in the GUI and run the emailer again.

---

## Setup

1. Clone the repo:

```bash
git clone https://github.com/uroojrafia4/ResumeMailer_GUI
cd Mini-ATS
```
2. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Create a .env file in the project root:

```bash
SENDER_EMAIL=youremail@example.com
SENDER_PASSWORD=yourpassword
```
4. Make sure you have a `resumes/` folder with resume files (PDF, DOCX, images) in this project folder.
5. **Logo in Emails (Optional):** To include an inline logo in emails, place `logo.png` in the same folder as the app. The emailer will automatically attach it if present.



### Email-Tempelate Setup:

- In emailer.py, there are two placeholder templates called "plain_text" and "html" for an html version and a plain text version in case html is disabled by the email client.
- After cloning the repo locally, replace the placeholders with your actual email templates.

---

## Usage

Run the GUI:
```bash
python main.py
```
1. Enter Job Title and Job Link.
2. Click Parse Resumes. Check the generated applicants.csv for correctness.
3. Click Send Emails to email applicants.

---

## Notes

- Emails are sent using the credentials in .env.
- Log file: Log_file.txt contains a record of all sent emails and errors.
- Weird formats: resumes that failed parsing are saved in weird_formats.txt.
- Parsing uses OCR for images; ensure scanned PDFs are clear for best results.

---

## Requirements

```bash
pymupdf
pytesseract
Pillow
python-docx
python-dotenv
```
Also install system Tesseract OCR:

- Ubuntu/Debian: sudo apt install tesseract-ocr
- Fedora: sudo dnf install tesseract
- macOS (Homebrew): brew install tesseract
