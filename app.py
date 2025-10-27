from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql@555777",   
        database="StudentCourseDB"
    )

# -------------------- HOMEPAGE --------------------
@app.route('/')
def home():
    return render_template("index.html")

# -------------------- STUDENTS --------------------
@app.route('/students')
def students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    conn.close()
    return render_template("students.html", students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Student (Name, Email, Phone, Department) VALUES (%s, %s, %s, %s)",
                   (request.form['name'], request.form['email'], request.form['phone'], request.form['dept']))
    conn.commit()
    conn.close()
    return redirect('/students')

@app.route('/update_student/<int:id>', methods=['POST'])
def update_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Student SET Name=%s, Email=%s, Phone=%s, Department=%s WHERE StudentID=%s",
                   (request.form['name'], request.form['email'], request.form['phone'], request.form['dept'], id))
    conn.commit()
    conn.close()
    return redirect('/students')

@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE StudentID=%s", (id,))
    conn.commit()
    conn.close()
    return redirect('/students')

# -------------------- COURSES --------------------
@app.route('/courses')
def courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Course.CourseID, Course.CourseName, Course.Credits, Course.Department, Faculty.Name AS FacultyName
        FROM Course
        LEFT JOIN Faculty ON Course.FacultyID = Faculty.FacultyID
    """)
    courses = cursor.fetchall()
    conn.close()
    return render_template("courses.html", courses=courses)

@app.route('/add_course', methods=['POST'])
def add_course():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Course (CourseName, Credits, Department, FacultyID) VALUES (%s, %s, %s, %s)",
                   (request.form['coursename'], request.form['credits'], request.form['dept'], request.form['facultyid']))
    conn.commit()
    conn.close()
    return redirect('/courses')

@app.route('/delete_course/<int:id>')
def delete_course(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Course WHERE CourseID=%s", (id,))
    conn.commit()
    conn.close()
    return redirect('/courses')

# -------------------- FACULTY --------------------
@app.route('/faculty')
def faculty():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Faculty")
    faculty = cursor.fetchall()
    conn.close()
    return render_template("faculty.html", faculty=faculty)

@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Faculty (Name, Email, Department) VALUES (%s, %s, %s)",
                   (request.form['name'], request.form['email'], request.form['dept']))
    conn.commit()
    conn.close()
    return redirect('/faculty')

@app.route('/delete_faculty/<int:id>')
def delete_faculty(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Faculty WHERE FacultyID=%s", (id,))
    conn.commit()
    conn.close()
    return redirect('/faculty')

# -------------------- REGISTRATIONS (JOIN QUERY) --------------------
@app.route('/registrations')
def registrations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all registrations (JOIN)
    cursor.execute("""
        SELECT Student.Name AS StudentName, Course.CourseName, Faculty.Name AS FacultyName, Registration.Semester
        FROM Registration
        JOIN Student ON Registration.StudentID = Student.StudentID
        JOIN Course ON Registration.CourseID = Course.CourseID
        JOIN Faculty ON Registration.FacultyID = Faculty.FacultyID
    """)
    data = cursor.fetchall()

    # Fetch Students, Courses, Faculty for dropdowns
    cursor.execute("SELECT StudentID, Name FROM Student")
    students = cursor.fetchall()
    cursor.execute("SELECT CourseID, CourseName FROM Course")
    courses = cursor.fetchall()
    cursor.execute("SELECT FacultyID, Name FROM Faculty")
    faculty = cursor.fetchall()

    conn.close()

    return render_template("registrations.html", data=data, students=students, courses=courses, faculty=faculty)


# -------------------- SEARCH REGISTERED STUDENT --------------------
@app.route('/search_registration', methods=['POST'])
def search_registration():
    keyword = request.form['keyword']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Student.Name AS StudentName, Course.CourseName, Faculty.Name AS FacultyName, Registration.Semester
        FROM Registration
        JOIN Student ON Registration.StudentID = Student.StudentID
        JOIN Course ON Registration.CourseID = Course.CourseID
        JOIN Faculty ON Registration.FacultyID = Faculty.FacultyID
        WHERE Student.Name LIKE %s OR Course.CourseName LIKE %s OR Faculty.Name LIKE %s
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()

    return render_template("registrations.html", data=results, search=keyword)

# -------------------- REGISTER A STUDENT INTO A COURSE --------------------
@app.route('/add_registration', methods=['POST'])
def add_registration():
    student_id = request.form['student_id']
    course_id = request.form['course_id']
    faculty_id = request.form['faculty_id']
    semester = request.form['semester']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Registration (StudentID, CourseID, FacultyID, Semester) VALUES (%s, %s, %s, %s)",
                   (student_id, course_id, faculty_id, semester))
    conn.commit()
    conn.close()

    return redirect('/registrations')





# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(debug=True)

