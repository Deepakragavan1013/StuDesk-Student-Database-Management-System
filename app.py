import streamlit as st
import mysql.connector
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Student Management System", layout="wide")

# Database Connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",  # Change this to your actual MySQL password
        database="StudentDB"
    )

# Authentication Function
def authenticate(email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Fetch All Students
def get_students():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["ID", "Name", "Age", "Department", "Email"])

# Add Student
def add_student(student_id, name, age, department, email):
    student_id = int(student_id)  # Ensure student_id is an integer
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Students (id, name, age, department, email) VALUES (%s, %s, %s, %s, %s)",
                   (student_id, name, age, department, email))
    conn.commit()
    conn.close()

# Delete Student (Fix: Convert ID to Python int)
def delete_student(student_id):
    student_id = int(student_id)  # Convert NumPy int64 to Python int
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE id=%s", (student_id,))
    conn.commit()
    conn.close()

# Update Student (Fix: Convert ID to Python int)
def update_student(student_id, name, age, department, email):
    student_id = int(student_id)  # Convert NumPy int64 to Python int
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Students SET name=%s, age=%s, department=%s, email=%s WHERE id=%s",
                   (name, age, department, email, student_id))
    conn.commit()
    conn.close()

# 🌟 **Login Section (Smaller, Centered)**
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 Login</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])  # Center login box
    with col2:
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        login_btn = st.button("Login")

    if login_btn:
        if authenticate(email, password):
            st.session_state.authenticated = True
            st.success("✅ Login Successful!")
            st.rerun()
        else:
            st.error("❌ Invalid Email or Password")

# 🌟 **Dashboard (After Login)**
else:
    st.sidebar.title("📌 Dashboard")
    menu = st.sidebar.radio("📂 Navigation", ["View Students", "Add Student", "Update Student", "Delete Student"])

    # 🔍 **Search Bar in Top Right**
    col1, col2 = st.columns([3, 1])  # Creates two columns
    with col2:
        search_term = st.text_input("🔍 Search Student by Name or ID", key="main_search")

    # 📄 **View Students**
    if menu == "View Students":
        st.subheader("📄 Student Records")
        students_df = get_students()

        # Filter Search Results
        if search_term:
            students_df = students_df[
                students_df["Name"].str.contains(search_term, case=False, na=False) |
                students_df["ID"].astype(str).str.contains(search_term, case=False, na=False)
            ]

        st.dataframe(students_df, use_container_width=True)

    # ➕ **Add Student**
    elif menu == "Add Student":
        st.subheader("➕ Add New Student")
        student_id = st.text_input("🎓 Student ID")
        name = st.text_input("👤 Name")
        age = st.number_input("📅 Age", min_value=1, max_value=100)
        department = st.text_input("🏛️ Department")
        email = st.text_input("📧 Email")
        if st.button("✅ Add Student"):
            add_student(student_id, name, age, department, email)
            st.success("🎉 Student Added Successfully!")

    # ✏️ **Update Student (By ID or Name)**
    elif menu == "Update Student":
        st.subheader("✏️ Update Student Details")

        # Single Search Field for ID or Name (Unique Key)
        search_input = st.text_input("🔍 Search Student by Name or ID", key="update_search")

        if search_input:
            students_df = get_students()

            # Search by ID or Name
            student_data = students_df[
                students_df["ID"].astype(str).str.contains(search_input, case=False, na=False) |
                students_df["Name"].str.contains(search_input, case=False, na=False)
            ]

            if not student_data.empty:
                student_id = int(student_data["ID"].values[0])  # Convert NumPy int64 to Python int
                name = st.text_input("👤 Name", student_data["Name"].values[0], key="update_name")
                age = st.number_input("📅 Age", min_value=1, max_value=100, value=int(student_data["Age"].values[0]), key="update_age")
                department = st.text_input("🏛️ Department", student_data["Department"].values[0], key="update_department")
                email = st.text_input("📧 Email", student_data["Email"].values[0], key="update_email")

                if st.button("💾 Update Student"):
                    update_student(student_id, name, age, department, email)
                    st.success(f"✅ Student '{name}' (ID: {student_id}) updated successfully!")
                    st.rerun()
            else:
                st.warning("⚠️ No matching student found.")

    # ❌ **Delete Student (By ID or Name)**
    elif menu == "Delete Student":
        st.subheader("❌ Delete Student")

        # Single Search Field for ID or Name (Unique Key)
        search_input = st.text_input("🔍 Search Student by Name or ID to Delete", key="delete_search")

        if search_input:
            students_df = get_students()

            # Search by ID or Name
            student_data = students_df[
                students_df["ID"].astype(str).str.contains(search_input, case=False, na=False) |
                students_df["Name"].str.contains(search_input, case=False, na=False)
            ]

            if not student_data.empty:
                student_id = int(student_data["ID"].values[0])  # Convert NumPy int64 to Python int
                student_name = student_data["Name"].values[0]  # Get student name
                st.write(f"**👤 Selected Student:** {student_name} (ID: {student_id})")

                if st.button("🗑️ Confirm Delete"):
                    delete_student(student_id)
                    st.success(f"✅ Student '{student_name}' (ID: {student_id}) deleted successfully!")
                    print("Deleted SucessfullyS")
                    st.rerun()
            else:
                st.warning("⚠️ No matching student found.")