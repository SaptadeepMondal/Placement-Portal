from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# MARK:ADMIN
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    def get_id(self):
        return f"admin-{self.id}"
    
# MARK:COMPANY
class Company(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    jobs = db.relationship('JobPosition', backref='company', lazy=True)
    def get_id(self):
        return f"company-{self.id}"

# MARK:STUDENT
class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    skills = db.Column(db.Text)
    education = db.Column(db.String(200))
    resume = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    applications = db.relationship('Application', backref='student', lazy=True)
    def get_id(self):
        return f"student-{self.id}"

# MARK:JOB POSITION
class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drive_name = db.Column(db.String(150))
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    status = db.Column(db.String(50), default="Pending")

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    applications = db.relationship('Application', backref='job', lazy=True)

# MARK:APPLICATION
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Applied")
    remarks = db.Column(db.String(200))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_position.id'))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_application'),
    )