import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import threading
import sys

from parser import parser  # your parser.py functions
# we import emailer lazily inside the thread to avoid import-time side-effects

# ---------- Main Window ----------
root = tk.Tk()
root.title("Mini ATS - Resume Parser")
root.geometry("600x420")
root.configure(bg="#2e2e2e")  # dark background

# ---------- Fonts & Colors ----------
LABEL_FONT = ("Helvetica", 11, "bold")
ENTRY_FONT = ("Helvetica", 11)
TEXT_BG = "#1e1e1e"
TEXT_FG = "#ffffff"
BUTTON_FONT = ("Helvetica", 11, "bold")

# ---------- Frames ----------
input_frame = tk.Frame(root, bg="#2e2e2e")
input_frame.pack(pady=10)

status_frame = tk.Frame(root, bg="#2e2e2e")
status_frame.pack(pady=10)

button_frame = tk.Frame(root, bg="#2e2e2e")
button_frame.pack(pady=5)

# ---------- Job Title & Link ----------
tk.Label(input_frame, text="Job Title:", font=LABEL_FONT, bg="#2e2e2e", fg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=5)
job_title_entry = tk.Entry(input_frame, width=50, font=ENTRY_FONT, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
job_title_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Job Link:", font=LABEL_FONT, bg="#2e2e2e", fg="#ffffff").grid(row=1, column=0, sticky="w", padx=5, pady=5)
job_link_entry = tk.Entry(input_frame, width=50, font=ENTRY_FONT, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
job_link_entry.grid(row=1, column=1, padx=5, pady=5)

# ---------- Status Box ----------
status_box = scrolledtext.ScrolledText(status_frame, width=70, height=14, font=("Courier", 10),
                                       bg=TEXT_BG, fg=TEXT_FG, insertbackground="#ffffff")
status_box.pack()

# ---------- Logging Helper ----------
def log_to_status(text):
    status_box.insert(tk.END, text + "\n")
    status_box.yview(tk.END)
    status_box.update()

# ---------- Stdout Redirector for running emailer in thread ----------
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        if not s:
            return
        # use after to safely update GUI from another thread
        def append():
            try:
                self.text_widget.insert(tk.END, s)
                self.text_widget.yview(tk.END)
            except tk.TclError:
                pass
        self.text_widget.after(0, append)
    def flush(self):
        pass

# ---------- Button Creator (kept as your original canvas look) ----------
def create_rounded_button(parent, text, bg_color, hover_color, command):
    canvas = tk.Canvas(parent, width=140, height=40, bg="#2e2e2e", highlightthickness=0)
    canvas.pack(side="left", padx=10)
    
    # Create rectangle (visual)
    x0, y0, x1, y1 = 2, 2, 138, 38
    button_bg = canvas.create_rectangle(x0, y0, x1, y1, fill=bg_color, outline=bg_color)
    canvas.create_text((x0+x1)//2, (y0+y1)//2, text=text, fill="white", font=BUTTON_FONT, tags="txt")
    
    # Hover effects
    def on_enter(event):
        canvas.itemconfig(button_bg, fill=hover_color, outline=hover_color)
    def on_leave(event):
        canvas.itemconfig(button_bg, fill=bg_color, outline=bg_color)
    canvas.tag_bind(button_bg, "<Enter>", on_enter)
    canvas.tag_bind(button_bg, "<Leave>", on_leave)
    canvas.tag_bind("txt", "<Enter>", on_enter)
    canvas.tag_bind("txt", "<Leave>", on_leave)
    
    # Click event
    def on_click(event):
        command()
    canvas.tag_bind(button_bg, "<Button-1>", on_click)
    canvas.tag_bind("txt", "<Button-1>", on_click)
    
    return canvas

# ---------- Parser Function ----------
def run_parser_gui():
    job_title = job_title_entry.get().strip()
    job_link = job_link_entry.get().strip()
    
    if not job_title or not job_link:
        messagebox.showerror("Input Error", "Please enter both Job Title and Job Link")
        return

    resumes_folder = "./resumes"
    if not os.path.exists(resumes_folder):
        messagebox.showerror("Folder Error", f"Folder '{resumes_folder}' not found!")
        return

    resumes = os.listdir(resumes_folder)
    log_to_status(f"Found {len(resumes)} resumes.")

    # Pass GUI logging function to parser
    weirds = parser(resumes, job_title, job_link, log_fn=log_to_status)

    if weirds:
        with open("weird_formats.txt", "w") as f:
            f.write("\n".join(weirds))
    
    log_to_status(f"Parsing done. {len(weirds)} weird format files.")
    if weirds:
        log_to_status(f"Weird formats: {', '.join(weirds)}")
    log_to_status("CSV generated: applicants.csv\n")

# ---------- Emailer integration ----------
emailer_running = False  # flag to prevent double runs

def _run_emailer_thread():
    """Thread target: import emailer, run activate_server(), redirect prints -> GUI."""
    global emailer_running
    if emailer_running:
        log_to_status("Emailer is already running.")
        return

    # Check CSV exists before starting
    if not os.path.exists("./applicants.csv"):
        log_to_status("applicants.csv not found. Run parser first.")
        return

    emailer_running = True
    # Redirect stdout/stderr to GUI status box
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = TextRedirector(status_box)
    sys.stderr = TextRedirector(status_box)
    try:
        # import here so main.py doesn't error if emailer.py has issues at import-time
        import emailer
        log_to_status("Starting email sending (see log here)...")
        # This will call emailer.activate_server() which internally opens SMTP and send_mail()
        emailer.activate_server()
        log_to_status("Email sending finished.")
    except Exception as e:
        # make sure exception is visible in GUI
        log_to_status(f"Emailer crashed: {e}")
    finally:
        # restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        emailer_running = False

def send_emails_gui():
    # Trigger the emailer in a background thread, with GUI log redirection
    if emailer_running:
        messagebox.showinfo("Already running", "Email sending is already in progress.")
        return

    # Basic guard: check if CSV exists
    if not os.path.exists("./applicants.csv"):
        messagebox.showerror("CSV Missing", "applicants.csv not found. Run the parser first.")
        return

    thread = threading.Thread(target=_run_emailer_thread, daemon=True)
    thread.start()
    log_to_status("Launched email sender thread...")

# ---------- Buttons ----------
create_rounded_button(button_frame, "Parse Resumes", "#4CAF50", "#5cb85c", run_parser_gui)
create_rounded_button(button_frame, "Send Emails", "#2196F3", "#42A5F5", send_emails_gui)

root.mainloop()
