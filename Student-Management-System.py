import sqlite3
import os
import tkinter as tk
import re
from datetime import datetime
from tkinter import ttk, messagebox, END

# Database Setup
script_dir = os.path.abspath(os.path.dirname(__file__) if "__file__" in globals() else os.getcwd())
db_path = os.path.join(script_dir, "students.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        birthday TEXT NOT NULL,
        address TEXT NOT NULL,
        gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
        degree_program TEXT NOT NULL,
        year_level INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4)
    )
""")
conn.commit()

# Predefined degree programs
DEGREE_PROGRAMS = ["Computer Science", "Information Technology", "Software Engineering", "Data Science", "Cybersecurity"]

BG_COLOR = "#2C3E50" 
FG_COLOR = "#ECF0F1"  
BUTTON_COLOR = "#3498DB"
HOVER_COLOR = "#2980B9" 

def clear_fields(self):
    self.entries["id"].delete(0, END)
    self.entries["full_name"].delete(0, END)
    self.entries["birthday"].delete(0, END)
    self.entries["address"].delete(0, END)
    self.entries["gender"].set("")
    self.entries["degree_program"].set("")
    self.entries["year_level"].set("")

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")

        # Set window size and center it
        width, height = 1000, 700
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x, y = (screen_width // 2) - (width // 2), (screen_height // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        root.configure(bg=BG_COLOR)

        # Apply ttk theme
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", HOVER_COLOR)], foreground=[("active", "white")])
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Title Label
        title = tk.Label(root, text="Student Management System", font=("Arial", 20, "bold"), fg=FG_COLOR, bg=BG_COLOR)
        title.pack(pady=10)

        # Form Frame
        form_frame = tk.Frame(root, bg=BG_COLOR)
        form_frame.pack(pady=10)

        fields = ["ID:", "Full Name:", "Birthday (MM/DD/YYYY):", "Address:", "Gender:", "Degree Program:", "Year Level:"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(form_frame, text=field, font=("Arial", 10), fg=FG_COLOR, bg=BG_COLOR).grid(row=i, column=0, sticky="w", padx=10, pady=5)

        self.entries["id"] = ttk.Entry(form_frame, width=30)
        self.entries["id"].grid(row=0, column=1, padx=10)

        self.entries["full_name"] = ttk.Entry(form_frame, width=30)
        self.entries["full_name"].grid(row=1, column=1, padx=10)

        self.entries["birthday"] = ttk.Entry(form_frame, width=30)
        self.entries["birthday"].grid(row=2, column=1, padx=10)

        self.entries["address"] = ttk.Entry(form_frame, width=30)
        self.entries["address"].grid(row=3, column=1, padx=10)

        self.entries["gender"] = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], width=28)
        self.entries["gender"].grid(row=4, column=1, padx=10)

        self.entries["degree_program"] = ttk.Combobox(form_frame, values=DEGREE_PROGRAMS, width=28)
        self.entries["degree_program"].grid(row=5, column=1, padx=10)

        self.entries["year_level"] = ttk.Combobox(form_frame, values=[1, 2, 3, 4], width=28)
        self.entries["year_level"].grid(row=6, column=1, padx=10)

        # Buttons Frame
        btn_frame = tk.Frame(root, bg=BG_COLOR)
        btn_frame.pack(pady=10)

        btn_texts = ["Add Student", "Update Student", "Delete Student", "Search by ID", "Show All"]
        btn_commands = [self.add_student, self.update_student, self.delete_student, self.search_student, self.show_all_students]

        for text, command in zip(btn_texts, btn_commands):
            ttk.Button(btn_frame, text=text, command=command, width=18).pack(side="left", padx=5, pady=5)


        # Filters Frame
        filter_frame = tk.Frame(root, bg=BG_COLOR)
        filter_frame.pack(pady=10)

        # Sort By
        tk.Label(filter_frame, text="Sort By:", fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, padx=5)
        self.sort_var = ttk.Combobox(filter_frame, values=["ID", "Name", "Year Level"])
        self.sort_var.grid(row=0, column=1, padx=5)

        # Filter by Year Level
        tk.Label(filter_frame, text="Year Level:", fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=2, padx=5)
        self.filter_year_var = ttk.Combobox(filter_frame, values=["All", 1, 2, 3, 4])
        self.filter_year_var.grid(row=0, column=3, padx=5)

        # Filter by Degree Program
        tk.Label(filter_frame, text="Degree Program:", fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=4, padx=5)
        self.filter_degree_var = ttk.Combobox(filter_frame, values=["All"] + DEGREE_PROGRAMS)
        self.filter_degree_var.grid(row=0, column=5, padx=5)

        # Apply Filters Button
        tk.Button(filter_frame, text="Apply Filters", command=self.apply_filters, font=("Arial", 10, "bold"),
                  fg="white", bg=BUTTON_COLOR, width=15).grid(row=0, column=6, padx=5)


        # Student Table Frame
        table_frame = tk.Frame(root)
        table_frame.pack(pady=10, fill="both", expand=True)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")

        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Student Table (Treeview)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Birthday", "Address", "Gender", "Program", "Year"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        self.tree.pack(fill="both", expand=True)

        # Configure Scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Set Column Headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=120, anchor="w")

    def add_student(self):
        try:
            # Get input values
            id = self.entries["id"].get().strip()
            name = self.entries["full_name"].get().strip()
            birthday = self.entries["birthday"].get().strip()
            address = self.entries["address"].get().strip()
            gender = self.entries["gender"].get().strip()
            degree = self.entries["degree_program"].get().strip()
            year = self.entries["year_level"].get().strip()

            # Validate Student ID: Must be a 6-digit number
            if not id.isdigit() or len(id) != 6:
                messagebox.showerror("Error", "Student ID must be a 6-digit number!")
                return
            id = int(id)  # Convert to integer after validation

            # Validate Full Name: Only letters and spaces allowed
            if not re.match(r"^[A-Za-z\s]+$", name):
                messagebox.showerror("Error", "Full Name must only contain letters and spaces!")
                return

            # Validate Birthday: Must be valid age
            try:
                if datetime.strptime(birthday, "%m/%d/%Y").year > datetime.now().year-16:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid Birthday! Invalid Birth Year.")
                return

            # Validate Birthday: Must be in MM/DD/YYYY format
            try:
                datetime.strptime(birthday, "%m/%d/%Y")
            except ValueError:
                messagebox.showerror("Error", "Invalid Birthday! Format must be MM/DD/YYYY.")
                return

            # Validate Year Level: Must be 1 to 4
            if not year.isdigit() or int(year) not in [1, 2, 3, 4]:
                messagebox.showerror("Error", "Year Level must be between 1 and 4!")
                return
            year = int(year)

            # Validate Gender: Must be selected from predefined options
            if gender not in ["Male", "Female", "Other"]:
                messagebox.showerror("Error", "Invalid Gender! Choose from Male, Female, or Other.")
                return

            # Validate Degree Program: Must be selected from predefined options
            if degree not in DEGREE_PROGRAMS:
                messagebox.showerror("Error", "Invalid Degree Program! Choose from the dropdown.")
                return

            # If all validations pass, insert the student into the database
            cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", 
                        (id, name, birthday, address, gender, degree, year))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.show_all_students()

            clear_fields(self)

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_student(self):
        id = self.entries["id"].get()

        # 🎯 Validation: Ensure ID is a 6-digit number
        if not id.isdigit() or len(id) != 6:
            messagebox.showerror("Error", "Student ID must be a 6-digit number!")
            return

        cursor.execute("SELECT * FROM students WHERE id=?", (id,))
        record = cursor.fetchone()

        if record:
            name = self.entries["full_name"].get() or record[1]
            birthday = self.entries["birthday"].get() or record[2]
            address = self.entries["address"].get() or record[3]
            gender = self.entries["gender"].get() or record[4]
            degree = self.entries["degree_program"].get() or record[5]
            year = self.entries["year_level"].get() or record[6]

            # Validate Birthday: Must be valid age
            try:
                if datetime.strptime(birthday, "%m/%d/%Y").year > datetime.now().year-16:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid Birthday! Invalid Birth Year.")
                return

            # Validate Birthday: Must be in MM/DD/YYYY format
            try:
                datetime.strptime(birthday, "%m/%d/%Y")
            except ValueError:
                messagebox.showerror("Error", "Invalid Birthday! Format must be MM/DD/YYYY.")
                return

            cursor.execute("""
                UPDATE students 
                SET full_name=?, birthday=?, address=?, gender=?, degree_program=?, year_level=? 
                WHERE id=?
            """, (name, birthday, address, gender, degree, int(year), id))
            conn.commit()
            messagebox.showinfo("Success", "Student record updated!")
            self.show_all_students()
        else:
            messagebox.showerror("Error", "Student not found!")
        
        clear_fields(self)

    def delete_student(self):
        id = self.entries["id"].get().strip()

        # Validate ID format
        if not id.isdigit() or len(id) != 6:
            messagebox.showerror("Error", "Student ID must be a 6-digit number!")
            return

        # Check if the student exists
        cursor.execute("SELECT * FROM students WHERE id=?", (id,))
        record = cursor.fetchone()

        if record:
            # Show confirmation dialog before deleting
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete student {record[1]}?")
            if confirm:
                cursor.execute("DELETE FROM students WHERE id=?", (id,))
                conn.commit()  # Save changes
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.show_all_students()
        else:
            messagebox.showerror("Error", "Student not found!")
        
        clear_fields(self)

    def search_student(self):
        id = self.entries["id"].get()
        cursor.execute("SELECT * FROM students WHERE id=?", (id,))
        record = cursor.fetchone()

        if record:
            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", "end", values=record)
        else:
            messagebox.showerror("Error", "Student not found!")
        
        clear_fields(self)

    def apply_filters(self):
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        # Filter by Year Level
        year_filter = self.filter_year_var.get()
        if year_filter and year_filter != "All":
            try:
                query += " AND year_level = ?"
                params.append(int(year_filter))
            except ValueError:
                messagebox.showerror("Error", "Invalid Year Level Selection!")
                return  # Stop execution if year filter is invalid

        # Filter by Degree Program
        degree_filter = self.filter_degree_var.get()
        if degree_filter and degree_filter != "All":
            query += " AND degree_program = ?"
            params.append(degree_filter)

        # Sorting
        sort_column_map = {"ID": "id", "Name": "full_name", "Year Level": "year_level"}
        sort_by = self.sort_var.get().strip()
        if sort_by in sort_column_map:
            query += f" ORDER BY {sort_column_map[sort_by]}"

        # Execute query
        cursor.execute(query, tuple(params))
        self.display_students(cursor.fetchall())
    
    def show_all_students(self):
        """Display all students in the table."""
        cursor.execute("SELECT * FROM students ORDER BY id")
        records = cursor.fetchall()
        self.display_students(records)

    def display_students(self, records):
        """Helper function to clear and display student records in the table."""
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", values=record)

    def on_exit(self):
        """Ensures database is committed and closed before exiting."""
        conn.commit()  # Ensure all changes are saved
        conn.close()   # Close connection
        self.root.destroy()  # Close the GUI

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()
