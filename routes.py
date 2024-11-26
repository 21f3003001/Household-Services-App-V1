# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import db, User, ServiceProfessional, Customer, Service
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Define a blueprint for routes
main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    return render_template('homepage.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        pincode = request.form.get('pincode')
        role = request.form.get('role', 'customer')  # Default to 'customer'

        # Validate form inputs
        if not username or not password or not confirm_password or not name or not address or not contact or not pincode:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('main.register'))
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.register'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create a new user instance
        new_user = User(
            username=username,
            password=hashed_password,
            name=name,
            address=address,
            contact=contact,
            pincode=pincode,
            role=role
        )
        
        try:
            # Save the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.register'))

    return render_template('register.html')


@main.route('/prof_register', methods=['GET', 'POST'])
def prof_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        pincode = request.form.get('pincode')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')

        # Validate form inputs
        if not username or not password or not confirm_password or not name or not address or not contact or not pincode or not service_type:
            flash('All fields except experience are required.', 'danger')
            return redirect(url_for('main.prof_register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('main.prof_register'))
        
        # Check if the username already exists
        existing_professional = ServiceProfessional.query.filter_by(username=username).first()
        if existing_professional:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.prof_register'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create a new service professional instance
        new_professional = ServiceProfessional(
            username=username,
            password=hashed_password,
            name=name,
            address=address,
            contact=contact,
            pincode=pincode,
            service_type=service_type,
            experience=experience,
            date_created=datetime.utcnow()
        )
        
        try:
            # Save the new professional to the database
            db.session.add(new_professional)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.prof_register'))

    # Fetch service types from the database
    services = Service.query.all()
    return render_template('prof_register.html', services=services)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  # Retrieve selected role

        # Query the database for the user with the selected role
        user = User.query.filter_by(username=username, role=role).first()

        # Check if the user exists and the password matches
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id

            # Redirect based on user role
            if user.role == "customer":
                return redirect(url_for('main.customer_dashboard'))
            elif user.role == "service_professional":
                return redirect(url_for('main.professional_dashboard'))
            elif user.role == "admin":
                return redirect(url_for('main.admin_dashboard'))  # Add an admin dashboard route if not already done

        else:
            flash("Invalid username, password, or role.", "danger")
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/customer_dashboard')
def customer_dashboard():
    services = Service.query.all()
    return render_template('user_panel/customer_dashboard.html', services=services)

@main.route('/professional_dashboard')
def professional_dashboard():
    return render_template('service_panel/professional_dashboard.html')

@main.route('/admin_dashboard')
def admin_dashboard():
     return redirect(url_for('admin.home'))
