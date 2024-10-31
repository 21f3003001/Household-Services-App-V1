# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import db, User, ServiceProfessional, Customer
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
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('main.register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Already registered!", "danger")
            return redirect(url_for('main.register'))

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == "service_professional":
            # Get additional professional details
            name = request.form.get('name')
            date_created = datetime.strptime(request.form.get('date_created'), '%Y-%m-%d')
            description = request.form.get('description')
            service_type = request.form.get('service_type')
            experience = request.form.get('experience')

            professional = ServiceProfessional(
                user_id=user.id,
                name=name,
                date_created=date_created,
                description=description,
                service_type=service_type,
                experience=experience
            )
            db.session.add(professional)
        elif role == "customer":
            customer = Customer(user_id=user.id)
            db.session.add(customer)

        db.session.commit()
        flash("Successfully registered!", "success")
        return redirect(url_for('main.register'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password matches
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id

            # Redirect based on user role
            if user.role == "customer":
                return redirect(url_for('main.customer_dashboard'))
            # Add other roles if necessary

            elif user.role == "service_professional":
                return redirect(url_for('main.professional_dashboard'))

            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard'))  # Or another page for different roles
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/customer_dashboard')
def customer_dashboard():
    return render_template('user_panel/customer_dashboard.html')

@main.route('/professional_dashboard')
def professional_dashboard():
    return render_template('service_panel/professional_dashboard.html')