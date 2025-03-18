import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import importlib
import nex1  # Imports everything from nex1.py

# Now you can call functions from nex1.py
nex1.function()  # Replace `some_function` with actual function name


# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",  # Change to your MySQL password
    database="StudentDB"
)
cursor = conn.cursor()



def insert_student():
    student_id = id_entry.get().strip()
    name = name_entry.get().strip()
    age = int(age_entry.get().strip())
    department = dept_entry.get().strip()
    email = email_entry.get().strip()

    # Debugging: Print values to see if they are empty
    print(f"ID: '{student_id}', Name: '{name}', Age: '{age}', Dept: '{department}', Email: '{email}'")

    if student_id and name and age and department and email:
        sql = "INSERT INTO Students (id, name, age, department, email) VALUES (%s, %s, %s, %s, %s)"
        values = (student_id, name, age, department, email)
        try:
            cursor.execute(sql, values)
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    else:
        messagebox.showerror("Error", "All fields are required!")

# Function to display students
def show_students():
    # Create a new window
    view_window = tk.Toplevel(root)
    view_window.title("Student Records")
    view_window.geometry("600x400")

    # Define columns for the table
    columns = ("ID", "Name", "Age", "Department", "Email")
    student_tree = ttk.Treeview(view_window, columns=columns, show="headings")

    # Set column headings
    for col in columns:
        student_tree.heading(col, text=col)
        student_tree.column(col, width=120)

    student_tree.pack(fill="both", expand=True)

    # Fetch all records from the database
    cursor.execute("SELECT * FROM Students")
    records = cursor.fetchall()

    # Insert data into the Treeview
    if records:  # Check if any data is retrieved
        for record in records:
            student_tree.insert("", "end", values=record)
    else:
        tk.Label(view_window, text="No records found", font=("Arial", 12)).pack()


# Function to update student
def update_student():
    student_id = id_entry.get()
    name = name_entry.get()
    age = age_entry.get()
    department = dept_entry.get()
    email = email_entry.get()

    if student_id and name and age and department and email:
        sql = "UPDATE Students SET name=%s, age=%s, department=%s, email=%s WHERE id=%s"
        values = (name, age, department, email, student_id)
        cursor.execute(sql, values)
        conn.commit()
        messagebox.showinfo("Success", "Student updated successfully!")
        clear_entries()
    else:
        messagebox.showerror("Error", "All fields are required!")

# Function to Delete Student
def delete_student(existing_window=None):
    delete_window = existing_window or tk.Toplevel(root)
    delete_window.title("Delete Student")
    delete_window.geometry("500x400")

    tk.Label(delete_window, text="Enter any field to delete student").pack(pady=5)

    # Entry Fields
    fields = ["ID", "Name", "Age", "Department", "Email"]
    entries = {}

    for field in fields:
        tk.Label(delete_window, text=f"{field}:").pack()
        entry = tk.Entry(delete_window)
        entry.pack()
        entries[field] = entry

    # Function to Perform Deletion
    def perform_delete():
        criteria = {field: entry.get().strip() for field, entry in entries.items()}
        criteria = {k: v for k, v in criteria.items() if v}  # Remove empty values

        if not criteria:
            messagebox.showerror("Error", "Enter at least one field to delete!")
            return

        query = "DELETE FROM Students WHERE " + " AND ".join(f"{key} = %s" for key in criteria)
        params = tuple(criteria.values())

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?"):
            try:
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    messagebox.showinfo("Success", "Student record deleted successfully!")
                else:
                    messagebox.showwarning("Not Found", "No matching record found to delete!")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

    # Delete Button
    if not existing_window:
        tk.Button(delete_window, text="Delete", command=perform_delete).pack(pady=10)


# Function to search student
def search_student():
    # Get input values from multiple entry fields
    search_id = id_entry.get().strip()
    search_name = name_entry.get().strip()
    search_age = age_entry.get().strip()
    search_dept = dept_entry.get().strip()
    search_email = email_entry.get().strip()

    # Check if at least one field is provided
    if not (search_id or search_name or search_age or search_dept or search_email):
        messagebox.showerror("Error", "Enter at least one value to search!")
        return

    # Build dynamic query
    query = "SELECT * FROM Students WHERE 1=1"
    params = []

    if search_id:
        query += " AND ID LIKE %s"
        params.append(f"%{search_id}%")
    if search_name:
        query += " AND Name LIKE %s"
        params.append(f"%{search_name}%")
    if search_age:
        query += " AND Age LIKE %s"
        params.append(f"%{search_age}%")
    if search_dept:
        query += " AND Department LIKE %s"
        params.append(f"%{search_dept}%")
    if search_email:
        query += " AND Email LIKE %s"
        params.append(f"%{search_email}%")

    # Execute query
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    if not records:
        messagebox.showinfo("Not Found", "No matching student records found!")
        return

    # Create a new window for search results
    search_window = tk.Toplevel(root)
    search_window.title("Search Results")
    search_window.geometry("600x400")

    # Define columns for the table
    columns = ("ID", "Name", "Age", "Department", "Email")
    student_tree = ttk.Treeview(search_window, columns=columns, show="headings")

    # Set column headings
    for col in columns:
        student_tree.heading(col, text=col)
        student_tree.column(col, width=120)

    student_tree.pack(fill="both", expand=True)

    # Insert matching records into the Treeview
    for record in records:
        student_tree.insert("", "end", values=record)

    # Scrollbar
    scrollbar = ttk.Scrollbar(search_window, orient="vertical", command=student_tree.yview)
    student_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")



# Function to clear entry fields
def clear_entries():
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    dept_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Student Database Management")

# Labels and Entry Fields
tk.Label(root, text="Student ID").grid(row=0, column=0)
tk.Label(root, text="Name").grid(row=1, column=0)
tk.Label(root, text="Age").grid(row=2, column=0)
tk.Label(root, text="Department").grid(row=3, column=0)
tk.Label(root, text="Email").grid(row=4, column=0)

id_entry = tk.Entry(root)
name_entry = tk.Entry(root)
age_entry = tk.Entry(root)
dept_entry = tk.Entry(root)
email_entry = tk.Entry(root)

id_entry.grid(row=0, column=1)
name_entry.grid(row=1, column=1)
age_entry.grid(row=2, column=1)
dept_entry.grid(row=3, column=1)
email_entry.grid(row=4, column=1)


# Buttons
tk.Button(root, text="Add Student", command=insert_student).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="View Students", command=show_students).grid(row=6, column=0, columnspan=2)
tk.Button(root, text="Update Student", command=update_student).grid(row=7, column=0, columnspan=2)
tk.Button(root, text="Delete student", command=delete_student).grid(row=8, column=0, columnspan=2)
tk.Button(root, text="Search Student", command=search_student).grid(row=9, column=0, columnspan=2)

# Display Area
display_text = tk.StringVar()
tk.Label(root, textvariable=display_text, justify=tk.LEFT).grid(row=10, column=0, columnspan=2)

root.mainloop()




