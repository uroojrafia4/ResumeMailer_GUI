import pymupdf, os, csv,re, pytesseract, sys
from PIL import Image
from docx import Document

resumes = os.listdir('./resumes')
print(f"Total number of resumes: {len(resumes)}")


with open("./applicants.csv", 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Email','Job Title', 'Job link'])

def clean_name(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'(?i)(resume|cv|final|copy|new|updated|profile)', '', name)
    name = re.sub(r'[\(\)\[\]\{\}_\-\.\d]+', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()
 
def save_to_csv(name, email, job_title, job_link):
    with open("./applicants.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, email, job_title, job_link])


def text_from_pdf(path):
    try:
        file = pymupdf.open(f"./resumes/{path}")
        text = file[0].get_text()
        if not text.strip():
            pix = file[0].get_pixmap()
            pix.save(temp:=f"./{os.path.splitext(path)[0]}_image.png")
            text = pytesseract.image_to_string(Image.open(temp))
            os.remove(temp)
        file.close()
        return text
    except Exception as e:
        print(f"An error ocurred with the PDF function {path}: ",e)

def text_from_docx(path):
    try:
        doc = Document(f"./resumes/{path}")
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)
    except Exception as e:
        print(f"An error ocurred with the DOCX function {path}: ",e)


def parser(resumes, job_title, job_link, log_fn=None):
    i = 0
    weirdFormat = []
    for resume in resumes:
        try:
            if resume.lower().endswith(('.png', '.jpg', '.jpeg')):
                text = pytesseract.image_to_string(Image.open(f"./resumes/{resume}"))
            elif resume.lower().endswith('.docx'):
                text = text_from_docx(resume)
            elif resume.lower().endswith('.pdf'):
                text = text_from_pdf(resume)
            else:
                weirdFormat.append(resume)
                if log_fn: log_fn("Invalid format")
                else: print("Invalid format")
                continue

            emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
            email = emails[0] if emails else None
            name = clean_name(resume)
            save_to_csv(name, email, job_title, job_link)
            i += 1
            if log_fn: log_fn(f"Saved {resume}'s data to csv!")
            else: print(f"Saved {resume}'s data to csv!")
        except Exception as e:
            if log_fn: log_fn(f"An error occurred with {resume}: {e}")
            else: print(f"An error occurred with {resume}: {e}")
    if log_fn: log_fn(f"Saved {i} resumes to csv!")
    else: print(f"Saved {i} resumes to csv!")
    return weirdFormat

# TODO
# add a fallback for name

    