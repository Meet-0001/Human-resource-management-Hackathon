"""
Dayflow HRMS - Main Application File
"""
from flask import Flask
from flask_login import LoginManager
from models import db, User
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dayflow-hrms-secret-key-2024'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dayflow_hrms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user from session"""
    return User.query.get(int(user_id))


# Register blueprints
from auth.routes import auth_bp
from routes.dashboard import dashboard_bp
from routes.profile import profile_bp
from routes.attendance import attendance_bp
from routes.leave import leave_bp
from routes.payroll import payroll_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(leave_bp, url_prefix='/leave')
app.register_blueprint(payroll_bp, url_prefix='/payroll')


def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


def init_sample_data():
    """Initialize sample data for testing"""
    from models import EmployeeProfile, Attendance, LeaveRequest, Payroll
    from datetime import datetime, date, timedelta
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("Sample data already exists. Skipping...")
            return
        
        # Create Admin user
        admin = User(
            employee_id='EMP001',
            email='admin@dayflow.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()
        
        admin_profile = EmployeeProfile(
            user_id=admin.id,
            first_name='John',
            last_name='Admin',
            phone='+1-234-567-8900',
            address='123 Admin Street, City, State 12345',
            date_of_birth=date(1985, 1, 15),
            department='Human Resources',
            position='HR Manager',
            hire_date=date(2020, 1, 1),
            employment_type='Full-time'
        )
        db.session.add(admin_profile)
        
        admin_payroll = Payroll(
            user_id=admin.id,
            base_salary=80000.0,
            allowances=10000.0,
            deductions=5000.0,
            net_salary=85000.0,
            effective_from=date(2024, 1, 1),
            currency='USD'
        )
        db.session.add(admin_payroll)
        
        # Create Employee users
        employees = [
            {
                'employee_id': 'EMP002',
                'email': 'employee1@dayflow.com',
                'password': 'emp123',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'department': 'Engineering',
                'position': 'Software Engineer',
                'salary': 75000.0
            },
            {
                'employee_id': 'EMP003',
                'email': 'employee2@dayflow.com',
                'password': 'emp123',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'department': 'Marketing',
                'position': 'Marketing Manager',
                'salary': 70000.0
            },
            {
                'employee_id': 'EMP004',
                'email': 'employee3@dayflow.com',
                'password': 'emp123',
                'first_name': 'Carol',
                'last_name': 'Williams',
                'department': 'Sales',
                'position': 'Sales Representative',
                'salary': 65000.0
            }
        ]
        
        for emp_data in employees:
            user = User(
                employee_id=emp_data['employee_id'],
                email=emp_data['email'],
                password_hash=generate_password_hash(emp_data['password']),
                role='employee'
            )
            db.session.add(user)
            db.session.flush()
            
            profile = EmployeeProfile(
                user_id=user.id,
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                phone=f'+1-234-567-{emp_data["employee_id"][-3:]}',
                address=f'{emp_data["first_name"]} Street, City, State',
                date_of_birth=date(1990, 5, 20),
                department=emp_data['department'],
                position=emp_data['position'],
                hire_date=date(2022, 6, 1),
                employment_type='Full-time'
            )
            db.session.add(profile)
            
            payroll = Payroll(
                user_id=user.id,
                base_salary=emp_data['salary'],
                allowances=emp_data['salary'] * 0.1,
                deductions=emp_data['salary'] * 0.05,
                net_salary=emp_data['salary'] * 1.05,
                effective_from=date(2024, 1, 1),
                currency='USD'
            )
            db.session.add(payroll)
            
            # Create some attendance records
            for i in range(5):
                att_date = date.today() - timedelta(days=i)
                attendance = Attendance(
                    user_id=user.id,
                    date=att_date,
                    check_in=datetime.combine(att_date, datetime.min.time().replace(hour=9)),
                    check_out=datetime.combine(att_date, datetime.min.time().replace(hour=17)),
                    status='present',
                    total_hours=8.0
                )
                db.session.add(attendance)
            
            # Create a leave request
            leave = LeaveRequest(
                user_id=user.id,
                leave_type='Paid',
                start_date=date.today() + timedelta(days=5),
                end_date=date.today() + timedelta(days=7),
                total_days=3,
                remarks='Family vacation',
                status='pending'
            )
            db.session.add(leave)
        
        db.session.commit()
        print("Sample data initialized successfully!")


if __name__ == '__main__':
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Create tables
    create_tables()
    
    # Initialize sample data
    init_sample_data()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

