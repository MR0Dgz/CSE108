import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

os.makedirs('data', exist_ok=True)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    courses = db.relationship('Course', backref='teacher', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    courses = db.relationship('CourseStudent', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    course_students = db.relationship('CourseStudent', backref='course', lazy=True)

class CourseStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    grade = db.Column(db.Integer)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        student = Student.query.filter_by(name=username).first()
        if student:
            session['username'] = username
            session['student_id'] = student.id
            return redirect(url_for('student_dashboard'))
        else:
            return "User not found", 404
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    student_courses = CourseStudent.query.filter_by(student_id=student_id).all()
    enrolled_courses_names = {course_student.course.name for course_student in student_courses}

    all_courses = db.session.query(Course).all()

    unique_courses = {}
    for course in all_courses:
        if course.name not in unique_courses:
            unique_courses[course.name] = course

    unique_courses_list = list(unique_courses.values())

    courses_with_status = []
    for course in unique_courses_list:
        status = "Drop" if course.name in enrolled_courses_names else "Add"
        courses_with_status.append((course, status))

    return render_template('student_dashboard.html', student_courses=student_courses, courses_with_status=courses_with_status)

@app.route('/add_course/<int:course_id>', methods=['POST'])
def add_course(course_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']
    course = Course.query.get_or_404(course_id)

    existing_enrollment = CourseStudent.query.filter_by(course_id=course_id, student_id=student_id).first()
    if existing_enrollment:
        return redirect(url_for('student_dashboard'))

    new_enrollment = CourseStudent(course_id=course_id, student_id=student_id)
    db.session.add(new_enrollment)
    db.session.commit()

    return redirect(url_for('student_dashboard'))

@app.route('/drop_course/<int:course_id>', methods=['POST'])
def drop_course(course_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']
    course = Course.query.get_or_404(course_id)
    
    enrollment = CourseStudent.query.filter_by(course_id=course_id, student_id=student_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()

    return redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


# def seed_database():    
#     print("Seeding database...")
#     teacher1 = Teacher(name="Ralph Jenkins")
#     teacher2 = Teacher(name="Susan Walker")
#     teacher3 = Teacher(name="Ammon Hepworth")

#     student1 = Student(name="Li Cheng")
#     student2 = Student(name="Betty Brown")
#     student3 = Student(name="Jose Santos")
#     student4 = Student(name="John Stuart")

#     student5 = Student(name="Nancy Little")
#     student6 = Student(name="Mindy Norris")
#     student7 = Student(name="Aditya Ranganath")
#     student8 = Student(name="Yi Wen Chen")

#     course1 = Course(name="Math 101", time="MWF 10:00- 10:50AM", capacity=8, teacher=teacher1)
#     course2 = Course(name="Physics 121", time="TR 11:00-11:50AM", capacity=10, teacher=teacher2)
#     course3 = Course(name="CS 106", time="MWF 2:00- 2:50PM", capacity=10, teacher=teacher3)
#     course4 = Course(name="CS 162", time="TR 3:00- 3:50PM", capacity=4, teacher=teacher3)

#     enrollment1 = CourseStudent(course=course1, student=student1, grade=77)
#     enrollment3 = CourseStudent(course=course1, student=student2, grade=65)
#     enrollment4 = CourseStudent(course=course1, student=student3, grade=92)
#     enrollment5 = CourseStudent(course=course1, student=student4, grade=86)


#     enrollment6 = CourseStudent(course=course2, student=student5, grade=53)
#     enrollment2 = CourseStudent(course=course2, student=student2, grade=88)
#     enrollment7 = CourseStudent(course=course2, student=student6, grade=94)
#     enrollment8 = CourseStudent(course=course2, student=student4, grade=91)
#     enrollment9 = CourseStudent(course=course2, student=student1, grade=85)

#     enrollment10 = CourseStudent(course=course3, student=student7, grade=93)
#     enrollment11 = CourseStudent(course=course3, student=student8, grade=85)
#     enrollment12 = CourseStudent(course=course3, student=student5, grade=57)
#     enrollment15 = CourseStudent(course=course3, student=student6, grade=68)

#     enrollment16 = CourseStudent(course=course4, student=student7, grade=99)
#     enrollment17 = CourseStudent(course=course4, student=student5, grade=87)
#     enrollment18 = CourseStudent(course=course4, student=student8, grade=92)
#     enrollment19 = CourseStudent(course=course4, student=student4, grade=67)


#     db.session.add_all([teacher1, teacher2, teacher3, student1, student2, student3, student4, student5, student6, student7, student8, course1, course2, course3, course4, enrollment1, enrollment2, enrollment3, enrollment4, enrollment5, enrollment6, enrollment7, enrollment8, enrollment9, enrollment10,enrollment11,  enrollment12, enrollment15, enrollment16, enrollment17, enrollment18, enrollment19])
#     db.session.commit()
#     print("Database seeding completed.")




if __name__ == '__main__':
    with app.app_context():
        db.create_all() 

        # seed_database() Leave as a comment, otherwise it will populate the database again even if entries alraedy exist!
    app.run(debug=True)
