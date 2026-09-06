from flask_login import UserMixin
from datetime import datetime, date, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


# Helper function to get current UTC time
def get_utc_now():
    return datetime.now(timezone.utc)


# Helper function to get current UTC date
def get_utc_today():
    return datetime.now(timezone.utc).date()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=get_utc_now)


class Performance(db.Model):
    __tablename__ = 'performances'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    score = db.Column(db.Float)
    time_spent_minutes = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=get_utc_now)
    week_number = db.Column(db.Integer)
    month_number = db.Column(db.Integer)
    year = db.Column(db.Integer)

    # Relationships
    student = db.relationship('User', backref='performances')
    module = db.relationship('Module', backref='performances')


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))
    points = db.Column(db.Integer, default=10)

    # Relationship
    module = db.relationship('Module', backref='quizzes')


class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=get_utc_today)
    status = db.Column(db.String(20), nullable=False)
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)  # Added check_out_time
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationship
    student = db.relationship('User', backref='attendances')


class Leave(db.Model):
    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    admin_remarks = db.Column(db.Text)
    applied_on = db.Column(db.DateTime, default=get_utc_now)
    reviewed_on = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(100), nullable=True)  # Changed to String, not ForeignKey

    # Relationship
    student = db.relationship('User', foreign_keys=[student_id], backref='leaves')