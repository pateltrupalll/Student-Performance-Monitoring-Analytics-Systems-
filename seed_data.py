"""
Run this file first to create database tables and add sample data
"""

from app import create_app, db
from app.models import User, Module, Quiz, Attendance, Leave
from datetime import datetime, date, timedelta, timezone


def seed_database():
    print("=" * 60)
    print("STUDENT PERFORMANCE SYSTEM - DATABASE SETUP")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # Drop all tables first (clean slate)
        print("\n📁 Resetting database...")
        db.drop_all()
        print("✓ Old tables dropped")

        # Create tables
        db.create_all()
        print("✓ New tables created successfully")

        # Create admin user
        print("\n👤 Creating admin user...")
        admin = User(
            username='admin',
            email='admin@school.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✓ Admin user created (username: admin, password: admin123)")

        # Create sample students
        print("\n👨‍🎓 Creating sample students...")
        students_data = [
            ('john_doe', 'john@example.com', 'password123'),
            ('jane_smith', 'jane@example.com', 'password123'),
            ('bob_wilson', 'bob@example.com', 'password123'),
            ('alice_brown', 'alice@example.com', 'password123'),
        ]

        student_objects = []
        for username, email, password in students_data:
            student = User(username=username, email=email, role='student')
            student.set_password(password)
            db.session.add(student)
            student_objects.append(student)
            print(f"✓ Student {username} created")

        db.session.commit()

        # Create modules with quizzes
        print("\n📚 Creating modules and quizzes...")

        # Module 1: Python Basics
        python_module = Module(
            module_name='Python Basics',
            description='Learn Python programming fundamentals including variables, loops, and functions',
            difficulty='Beginner',
            duration_minutes=120
        )
        db.session.add(python_module)
        db.session.flush()

        quiz1 = Quiz(
            module_id=python_module.id,
            question="What is the correct way to create a function in Python?",
            option_a="function myFunction():",
            option_b="def myFunction():",
            option_c="create myFunction():",
            option_d="new myFunction():",
            correct_answer="B",
            points=10
        )
        quiz2 = Quiz(
            module_id=python_module.id,
            question="Which of the following is used for comments in Python?",
            option_a="//",
            option_b="/* */",
            option_c="#",
            option_d="<!-- -->",
            correct_answer="C",
            points=10
        )
        db.session.add(quiz1)
        db.session.add(quiz2)
        print("✓ Module 'Python Basics' created with 2 quizzes")

        # Module 2: SQL Fundamentals
        sql_module = Module(
            module_name='SQL Fundamentals',
            description='Learn to write SQL queries and manage databases',
            difficulty='Beginner',
            duration_minutes=150
        )
        db.session.add(sql_module)
        db.session.flush()

        quiz3 = Quiz(
            module_id=sql_module.id,
            question="Which SQL statement is used to extract data from a database?",
            option_a="GET",
            option_b="SELECT",
            option_c="EXTRACT",
            option_d="OPEN",
            correct_answer="B",
            points=10
        )
        db.session.add(quiz3)
        print("✓ Module 'SQL Fundamentals' created with 1 quiz")

        db.session.commit()

        # Create sample attendance records
        print("\n📋 Creating sample attendance records...")
        today = date.today()
        for student in student_objects:
            # Create attendance for the last 5 days
            for i in range(5):
                attendance_date = today - timedelta(days=i)
                # Skip weekends for demo
                if attendance_date.weekday() < 5:  # Monday to Friday
                    status = 'Present' if i % 3 != 0 else 'Absent'
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        check_in_time=datetime.now(timezone.utc).time(),
                        remarks='Sample attendance record'
                    )
                    db.session.add(attendance)
            print(f"✓ Attendance records created for {student.username}")

        db.session.commit()

        # Create sample leave applications
        print("\n📝 Creating sample leave applications...")
        for student in student_objects[:2]:
            leave = Leave(
                student_id=student.id,
                start_date=today + timedelta(days=5),
                end_date=today + timedelta(days=7),
                leave_type='Sick',
                reason='Not feeling well, need rest',
                status='Pending'
            )
            db.session.add(leave)
            print(f"✓ Leave application created for {student.username}")

        db.session.commit()

        print("\n" + "=" * 60)
        print("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📝 LOGIN CREDENTIALS:")
        print("   👑 Admin:  username='admin', password='admin123'")
        print("   👨‍🎓 Student: username='john_doe', password='password123'")
        print("   👩‍🎓 Student: username='jane_smith', password='password123'")
        print("   👨‍🎓 Student: username='bob_wilson', password='password123'")
        print("   👩‍🎓 Student: username='alice_brown', password='password123'")
        print("\n✨ FEATURES AVAILABLE:")
        print("   ✅ Student Dashboard - View performance, attendance, leaves")
        print("   ✅ Take Quizzes - Complete modules and get scores")
        print("   ✅ Mark Attendance - Daily attendance tracking")
        print("   ✅ Apply Leave - Submit leave applications")
        print("   ✅ Admin Panel - Manage all students, attendance, leaves")
        print("\n🌐 To start the application, run: python run.py")
        print("=" * 60)


if __name__ == '__main__':
    seed_database()