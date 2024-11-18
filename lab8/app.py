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

def seed_database():
    if Teacher.query.first():
        print("Database already seeded. Skipping...")
        return
    
    print("Seeding database...")
    teacher1 = Teacher(name="Ralph Jenkins")
    teacher2 = Teacher(name="Susan Walker")
    teacher3 = Teacher(name="Ammon Hepworth")
    student1 = Student(name="Li Cheng")
    student2 = Student(name="Betty Brown")
    course1 = Course(name="Math 101", time="MWF 10:00- 10:50AM", capacity=8, teacher=teacher1)
    course2 = Course(name="Physics 121", time="TR 11:00-11:50AM", capacity=10, teacher=teacher2)
    enrollment1 = CourseStudent(course=course1, student=student1, grade=77)
    enrollment2 = CourseStudent(course=course2, student=student2, grade=88)
    enrollment3 = CourseStudent(course=course1, student=student2, grade=65)

    db.session.add_all([teacher1, teacher2, student1, student2, course1, course2, enrollment1, enrollment2, enrollment3])
    db.session.commit()
    print("Database seeding completed.")



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 

        seed_database()
    app.run(debug=True)
