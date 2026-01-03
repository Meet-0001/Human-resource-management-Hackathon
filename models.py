"""
Database Models for Dayflow HRMS
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'employee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('EmployeeProfile', backref='user', uselist=False)
    attendance_records = db.relationship('Attendance', backref='user', lazy=True, foreign_keys='Attendance.user_id')
    leave_requests = db.relationship('LeaveRequest', backref='user', lazy=True, foreign_keys='LeaveRequest.user_id')
    payroll = db.relationship('Payroll', backref='user', lazy=True, foreign_keys='Payroll.user_id')
    
    # Relationship for reviews (admin who reviewed leave requests)
    reviewed_leaves = db.relationship('LeaveRequest', backref='reviewer', lazy=True, foreign_keys='LeaveRequest.reviewed_by')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)


class EmployeeProfile(db.Model):
    """Employee profile information"""
    __tablename__ = 'employee_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Personal Details
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    profile_picture = db.Column(db.String(255))  # Path to image file
    
    # Job Details
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    employment_type = db.Column(db.String(50))  # Full-time, Part-time, Contract
    
    # Documents (placeholder - store paths or references)
    documents = db.Column(db.Text)  # JSON string of document paths
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Attendance(db.Model):
    """Employee attendance records"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Check-in/out times
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    
    # Attendance status
    status = db.Column(db.String(20), default='absent')  # present, absent, half-day, leave
    
    # Working hours
    total_hours = db.Column(db.Float, default=0.0)
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one record per user per day
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)


class LeaveRequest(db.Model):
    """Leave request management"""
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Leave details
    leave_type = db.Column(db.String(50), nullable=False)  # Paid, Sick, Unpaid
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    
    # Request details
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Admin response
    admin_comments = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payroll(db.Model):
    """Employee payroll and salary information"""
    __tablename__ = 'payroll'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Salary details
    base_salary = db.Column(db.Float, nullable=False)
    allowances = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, nullable=False)
    
    # Pay period
    pay_period_start = db.Column(db.Date)
    pay_period_end = db.Column(db.Date)
    
    # Additional info
    currency = db.Column(db.String(10), default='USD')
    notes = db.Column(db.Text)
    
    # Effective date
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date, nullable=True)  # NULL means currently active
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

