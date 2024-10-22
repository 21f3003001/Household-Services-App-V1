from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, User, Professional
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    return render_template('homepage.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Professional-specific fields (Corrected to use .get())
        name = request.form.get('name')  # Fixed the issue here
        description = request.form.get('description')
        service_type = request.form.get('service_type')
        service_category = request.form.get('service_category')
        experience = request.form.get('experience')

        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('main.register'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already registered. Please login or use a different username.', 'error')
            return redirect(url_for('main.register'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Create the user/professional
        if role == 'professional':
            # Creating a Professional with extra fields
            new_user = User(
                username=username,
                password=hashed_password,
                role=role,
                name=name,
                description=description,
                service_type=service_type,
                service_category=service_category,
                experience=experience,
                date_created=datetime.now()
            )
        else:
            # Creating a Customer
            new_user = User(
                username=username,
                password=hashed_password,
                role=role,
                date_created=datetime.now()
            )

        # Add user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('main.register'))
    
    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']

        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            # You can log the user in here (e.g., using Flask-Login) and redirect to the dashboard
            return redirect(url_for('main.homepage'))
        else:
            flash('Login failed. Please check your email and password.', 'error')
    
    return render_template('login.html')
