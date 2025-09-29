import smtplib, csv, time, random, datetime,os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SERVER = "smtp.gmail.com" 
PORT = 465

def send_mail(server):
    with open("./applicants.csv","r") as f:
        reader = csv.DictReader(f)
        print("Sending mails...")
        i = 0
        for person in reader:
            try:
                TO = person["Email"]
                if not TO:
                    with open("Log_file.txt", "a") as f:
                        f.write(f"No email found for {i+1}th person\n\n")
                    continue 
                NAME = person["Name"]
                first_name = NAME.split()[0] if NAME else "there"
                JOB_TITLE = person["Job Title"] if person["Job Title"] != '' else "No Job Title"
                JOB_LINK = person["Job link"] if person["Job link"] != '' else "No Job link"

                msg = MIMEMultipart("related")
                msg["Subject"] = f"{JOB_TITLE} Application"
                msg["From"] = SENDER_EMAIL
                msg["To"] = TO

                # create alternative container for plain + html
                alt_part = MIMEMultipart("alternative")


                # Attach plain text and HTML versions
                plain_text = f"""YOUR PLAIN TEXT EMAIL TEMPELATE HERE.
                Example: Hi {first_name},

                    Thank you for applying to the {JOB_TITLE} role!

                    Please finalize your application using the following link:
                    {JOB_LINK}

                    Best Regards,
                    Your Name
                    """

                html = f"""YOUR HTML EMAIL TEMPELATE HERE.
                Example:  !DOCTYPE html>
                    <html>
                    <body>
                        <p>Hi {first_name},</p>
                        <p>Thank you for applying to the {JOB_TITLE} role!</p>
                        <p>Please finalize your application using the following link:</p>
                        <p><a href="{JOB_LINK}" target="_blank">{JOB_TITLE} application</a></p>
                        <p>Best Regards,<br/>
                        Your Name</p>
                    </body>
                    </html>"""
                                    
                alt_part.attach(MIMEText(plain_text, "plain"))
                alt_part.attach(MIMEText(html, "html"))
                msg.attach(alt_part)
                
                logo_path = "./logo.png"
                if os.path.exists(logo_path):
                    with open("./logo.png", "rb") as img:  
                        logo = MIMEImage(img.read())
                        logo.add_header("Content-ID", "<companylogo>")
                        logo.add_header("Content-Disposition", "inline", filename="logo.png")
                        msg.attach(logo)

                server.sendmail(SENDER_EMAIL, TO, msg.as_string())
                i+=1
                print(f"Email sent to: {TO}, {NAME}")
                with open("Log_file.txt", "a") as f:
                    f.write(f"✅ Email successfully sent to,\n name: {NAME}\n email: {TO}\n from: {SENDER_EMAIL}\n job: {JOB_TITLE}\n at: {datetime.datetime.now()}\n\n")
                
                time.sleep(random.uniform(30,75))
            except Exception as e:
                print(f"An error ocurred with email: {TO}, error: {e}")
                with open("Log_file.txt", "a") as f:
                    f.write(f"Error with\nemail: {TO}\nname: {NAME}\nerror: {e}\n\n")
        return i
def activate_server():
    with smtplib.SMTP_SSL(SERVER, PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("✅ Connected to the server!")
        count = send_mail(server)
        print(f"🎉 Successfully sent {count} emails!")



