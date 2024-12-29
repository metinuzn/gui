import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random

font_main = ("Arial", 12, "bold")
font_title = ("Arial", 14, "bold")

conn = sqlite3.connect('student_registration.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
    student_number TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    password TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
    course_code TEXT PRIMARY KEY,
    course_name TEXT,
    ects_points INTEGER,
    instructor TEXT,
    day TEXT,
    time TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
    student_number TEXT,
    course_code TEXT,
    PRIMARY KEY (student_number, course_code),
    FOREIGN KEY (student_number) REFERENCES students(student_number),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
)''')

courses = [
    ("CS101", "Introduction to Programming", 6),
    ("MATH201", "Calculus II", 5),
    ("PHYS301", "Quantum Physics", 4),
    ("HIST102", "World History", 3),
    ("BIO202", "Molecular Biology", 6),
    ("CHEM101", "General Chemistry", 4),
    ("ENG101", "English Composition", 3),
    ("ECON201", "Microeconomics", 3),
    ("POLS101", "Introduction to Political Science", 3),
    ("SOC101", "Introduction to Sociology", 3),
    ("ART101", "Art History", 3),
    ("MUS101", "Music Appreciation", 3),
    ("PHIL101", "Introduction to Philosophy", 3),
    ("PSY101", "Introduction to Psychology", 3),
    ("GEOG101", "World Geography", 3)
]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
hours = ["09:00-10:30", "10:45-12:15", "13:30-15:00", "15:15-16:45"]

instructors = ["Dr. Engin Karaman", "Dr. Deniz Gezmis", "Dr. Jose Mourinho", "Prof. Dr. Jorge Jesus", "Dr. Vitor Pereira"]

for course in courses:
    cursor.execute("INSERT OR IGNORE INTO courses (course_code, course_name, ects_points, instructor, day, time) VALUES (?, ?, ?, ?, ?, ?)", 
                   (course[0], course[1], course[2], random.choice(instructors), random.choice(days), random.choice(hours)))

conn.commit()

def generate_student_number():
    return str(random.randint(1000000000, 9999999999))

def get_first_name(full_name):
    return full_name.split()[0] if ' ' in full_name else full_name

def register_student():
    full_name = entry_name.get()
    last_name = entry_surname.get()
    password = entry_password.get()

    if not full_name or not last_name or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    first_name = get_first_name(full_name)
    student_number = generate_student_number()
    email = f"{first_name.lower()}.{last_name.lower()}@stu.fbu.edu.tr"

    try:
        cursor.execute("INSERT INTO students (student_number, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)",
                       (student_number, first_name, last_name, email, password))
        conn.commit()
        
        result_frame = tk.Frame(frame_register, bg="gray")
        result_frame.pack(pady=10)

        result_text = f"Registration successful!\nYour student number: {student_number}\nYour email: {email}"
        result_label = tk.Label(result_frame, text=result_text, bg="gray", fg="white")
        result_label.pack(pady=5)

        def copy_to_clipboard():
            root.clipboard_clear()
            root.clipboard_append(result_text)
            root.update()

        copy_button = tk.Button(result_frame, text="Copy", command=copy_to_clipboard)
        copy_button.pack()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Student number already exists. Try again.")

def login():
    student_number = entry_login_number.get()
    email = entry_login_email.get()
    password = entry_login_password.get()

    cursor.execute("SELECT * FROM students WHERE student_number = ? AND email = ? AND password = ?",
                   (student_number, email, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Success", "Login successful!")
        frame_login.pack_forget()
        open_course_registration(result[0])
        root.withdraw()
    else:
        messagebox.showerror("Error", "Invalid credentials. Please try again.")

def open_course_registration(student_number):
    course_window = tk.Toplevel(root)
    course_window.title("Course Registration")
    course_window.configure(bg="#00205B")

    def go_back():
        course_window.destroy()
        root.deiconify()

    back_button = tk.Button(course_window, text="Back", command=go_back)
    back_button.pack(pady=5)

    label_courses = tk.Label(course_window, text="Available Courses", font=font_title, bg="#00205B", fg="white")
    label_courses.pack(pady=10)

    tree = ttk.Treeview(course_window, columns=("Course Code", "Course Name", "ECTS Points", "Instructor", "Day", "Time"), show="headings", height=10)
    tree.heading("Course Code", text="Course Code")
    tree.heading("Course Name", text="Course Name")
    tree.heading("ECTS Points", text="ECTS Points")
    tree.heading("Instructor", text="Instructor")
    tree.heading("Day", text="Day")
    tree.heading("Time", text="Time")
    tree.pack(pady=10)

    cursor.execute("SELECT * FROM courses")
    all_courses = cursor.fetchall()

    cursor.execute("SELECT course_code FROM registrations WHERE student_number = ?", (student_number,))
    registered_courses = {row[0] for row in cursor.fetchall()}

    for course in all_courses:
        tags = ("selected",) if course[0] in registered_courses else ("",)
        tree.insert("", tk.END, values=course, tags=tags)

    tree.tag_configure("selected", background="lightgreen")

    selected_courses_frame = tk.Frame(course_window, bg="#00205B")
    selected_courses_frame.pack(pady=10, fill=tk.X)

    selected_courses_label = tk.Label(selected_courses_frame, text="Selected Courses:", font=font_main, bg="#00205B", fg="white")
    selected_courses_label.pack(pady=5)

    selected_courses_listbox = tk.Listbox(selected_courses_frame, font=("Arial", 12))
    for course_code in registered_courses:
        selected_courses_listbox.insert(tk.END, course_code)
    selected_courses_listbox.pack(fill=tk.X, padx=10)

    def add_course():
        selected_item = tree.selection()
        if selected_item:
            course = tree.item(selected_item, "values")
            course_code = course[0]
            if course_code not in registered_courses:
                selected_courses_listbox.insert(tk.END, course_code)
                registered_courses.add(course_code)
                tree.item(selected_item, tags=("selected",))

    def remove_course():
        selected_index = selected_courses_listbox.curselection()
        if selected_index:
            course_code = selected_courses_listbox.get(selected_index)
            selected_courses_listbox.delete(selected_index)
            registered_courses.discard(course_code)

            for item in tree.get_children():
                if tree.item(item, "values")[0] == course_code:
                    tree.item(item, tags=("",))

    def show_schedule():
        schedule_window = tk.Toplevel(course_window)
        schedule_window.title("Schedule")
        schedule_window.configure(bg="#00205B")

        schedule_label = tk.Label(schedule_window, text="Your Schedule", font=("Arial", 14, "bold"), bg="#00205B", fg="white")
        schedule_label.pack(pady=10)

        schedule_frame = tk.Frame(schedule_window, bg="#00205B")
        schedule_frame.pack(pady=10)

        tk.Label(schedule_frame, text="Day", bg="#FFD700", fg="black", width=15, font=("Arial", 10, "bold"), relief="solid").grid(row=0, column=0)
        tk.Label(schedule_frame, text="Time", bg="#FFD700", fg="black", width=20, font=("Arial", 10, "bold"), relief="solid").grid(row=0, column=1)
        tk.Label(schedule_frame, text="Course", bg="#FFD700", fg="black", width=30, font=("Arial", 10, "bold"), relief="solid").grid(row=0, column=2)

        cursor.execute("SELECT courses.day, courses.time, courses.course_name FROM courses JOIN registrations ON courses.course_code = registrations.course_code WHERE registrations.student_number = ?", (student_number,))
        schedule = cursor.fetchall()

        for i, (day, time, course_name) in enumerate(schedule, start=1):
            tk.Label(schedule_frame, text=day, bg="white", fg="black", width=15, font=("Arial", 10), relief="solid").grid(row=i, column=0)
            tk.Label(schedule_frame, text=time, bg="white", fg="black", width=20, font=("Arial", 10), relief="solid").grid(row=i, column=1)
            tk.Label(schedule_frame, text=course_name, bg="white", fg="black", width=30, font=("Arial", 10), relief="solid").grid(row=i, column=2)

    add_button = tk.Button(course_window, text="Add Course", command=add_course, bg="#00205B", fg="white",
                           activebackground="#FFD700", activeforeground="black", font=font_main)
    add_button.pack(pady=5)

    remove_button = tk.Button(course_window, text="Remove Course", command=remove_course, bg="#00205B", fg="white",
                              activebackground="#FFD700", activeforeground="black", font=font_main)
    remove_button.pack(pady=5)

    show_schedule_button = tk.Button(course_window, text="Show Schedule", command=show_schedule, bg="#00205B", fg="white",
                                     activebackground="#FFD700", activeforeground="black", font=font_main)
    show_schedule_button.pack(pady=10)

    def save_courses():
        # Clear existing registrations
        cursor.execute("DELETE FROM registrations WHERE student_number = ?", (student_number,))

        for course_code in registered_courses:
            cursor.execute("INSERT INTO registrations (student_number, course_code) VALUES (?, ?)",
                           (student_number, course_code))

        conn.commit()
        messagebox.showinfo("Success", "Courses registered successfully!")

    button_save = tk.Button(course_window, text="Save Courses", command=save_courses, bg="#00205B", fg="white",
                            activebackground="#FFD700", activeforeground="black", font=font_main)
    button_save.pack(pady=10)

root = tk.Tk()
root.title("Student Registration System")
root.configure(bg="#00205B")

style = ttk.Style()
style.theme_create("FenerbahceTheme", parent="alt", settings={
    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
    "TNotebook.Tab": {
        "configure": {"padding": [80, 1], "background": "#00205B", "foreground": "white"},
        "map":       {"background": [("selected", "#FFD700")],
                       "foreground": [("selected", "black")],
                       "expand": [("selected", [1, 1, 1, 0])] } } } )
style.theme_use("FenerbahceTheme")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=20, pady=20)

frame_register = tk.Frame(notebook)
notebook.add(frame_register, text="Register")

frame_register.configure(bg="#FFD700" if style.lookup("TNotebook.Tab", "background") == "#00205B" else "#00205B")

label_register = tk.Label(frame_register, text="Register", font=("Arial", 20, "bold"), bg=frame_register["background"], fg="black")
label_register.pack(pady=10)

label_name = tk.Label(frame_register, text="Full Name:", font=font_title, bg=frame_register["background"], fg="black")
label_name.pack(pady=5)
entry_name = tk.Entry(frame_register, font=font_title)
entry_name.pack(pady=5)

label_surname = tk.Label(frame_register, text="Last Name:", font=("Arial", 14), bg=frame_register["background"], fg="black")
label_surname.pack(pady=5)
entry_surname = tk.Entry(frame_register, font=("Arial", 14))
entry_surname.pack(pady=5)

label_password = tk.Label(frame_register, text="Password:", font=("Arial", 14), bg=frame_register["background"], fg="black")
label_password.pack(pady=5)
entry_password = tk.Entry(frame_register, show="*", font=("Arial", 14))
entry_password.pack(pady=5)

button_register = tk.Button(frame_register, text="Register", command=register_student, bg="#00205B", fg="white",
                           activebackground="#FFD700", activeforeground="black", font=("Arial", 14, "bold"))
button_register.pack(pady=10)

frame_login = tk.Frame(notebook)
notebook.add(frame_login, text="Login")

frame_login.configure(bg="#FFD700" if style.lookup("TNotebook.Tab", "background") == "#00205B" else "#00205B")

label_login = tk.Label(frame_login, text="Login", font=("Arial", 20, "bold"), bg=frame_login["background"], fg="black")
label_login.pack(pady=10)

label_login_number = tk.Label(frame_login, text="Student Number:", font=("Arial", 14), bg=frame_login["background"], fg="black")
label_login_number.pack(pady=5)
entry_login_number = tk.Entry(frame_login, font=("Arial", 14))
entry_login_number.pack(pady=5)

label_login_email = tk.Label(frame_login, text="Email:", font=("Arial", 14), bg=frame_login["background"], fg="black")
label_login_email.pack(pady=5)
entry_login_email = tk.Entry(frame_login, font=("Arial", 14))
entry_login_email.pack(pady=5)

label_login_password = tk.Label(frame_login, text="Password:", font=("Arial", 14), bg=frame_login["background"], fg="black")
label_login_password.pack(pady=5)
entry_login_password = tk.Entry(frame_login, show="*", font=("Arial", 14))
entry_login_password.pack(pady=5)

button_login = tk.Button(frame_login, text="Login", command=login, bg="#00205B", fg="white",
                         activebackground="#FFD700", activeforeground="black", font=("Arial", 14, "bold"))
button_login.pack(pady=10)

root.mainloop()

conn.close()
