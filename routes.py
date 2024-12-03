# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import db, User, ServiceProfessional, Customer, Service, ServiceRequest
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
        user_name = request.form.get('user_name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        pincode = request.form.get('pincode')
        role = request.form.get('role', 'customer')  # Default to 'customer'

        # Validate form inputs
        if not username or not password or not confirm_password or not user_name or not address or not contact or not pincode:
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
            user_name=user_name,
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
        prof_name = request.form.get('prof_name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        pincode = request.form.get('pincode')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')
        role = request.form.get('role', 'service_professional')

        # Validate form inputs
        if not username or not password or not confirm_password or not prof_name or not address or not contact or not pincode or not service_type:
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
            prof_name=prof_name,
            address=address,
            contact=contact,
            pincode=pincode,
            service_type=service_type,
            experience=experience,
            date_created=datetime.utcnow(),
            role=role
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

        # Query the correct table based on role
        if role == "customer":
            user = User.query.filter_by(username=username, role="customer").first()
        elif role == "service_professional":
            user = ServiceProfessional.query.filter_by(username=username, role="service_professional").first()  # No 'role' column in this table
        elif role == "admin":
            user = User.query.filter_by(username=username, role="admin").first()
        else:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('main.login'))

        # Check if the user exists and the password matches
        if user and check_password_hash(user.password, password):
            # Check if the user is blocked (for 'customer' and 'admin' roles only)
            if role in ["customer", "admin"] and user.status == "Blocked":
                flash("Your account has been blocked. Please contact support.", "danger")
                return redirect(url_for('main.login'))

            # Store user details in session
            if role == "customer" or role == "admin":
                # For 'User' table roles
                session['user_id'] = user.user_id
                session['username'] = user.username
                session['role'] = role
            elif role == "service_professional":
                # For 'ServiceProfessional' table
                session['prof_id'] = user.prof_id
                session['username'] = user.username
                session['role'] = role

            # Redirect based on user role
            if role == "customer":
                return redirect(url_for('main.customer_dashboard'))
            elif role == "service_professional":
                return redirect(url_for('main.professional_dashboard'))
            elif role == "admin":
                return redirect(url_for('main.admin_dashboard'))

        # Invalid credentials
        flash("Invalid username, password, or role.", "danger")
        return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/customer_dashboard')
def customer_dashboard():
    return redirect(url_for('customer.dashboard'))

@main.route('/professional_dashboard')
def professional_dashboard():
    services = Service.query.all()
    # Fetch logged-in professional's ID from session
    prof_id = session.get('prof_id')
    if not prof_id:
        flash("You must be logged in to view your dashboard.", "danger")
        return redirect(url_for('main.login'))  # Redirect to login page if not logged in

    # Fetch today's requested services (status: 'Requested')
    today_services = (
        db.session.query(
            ServiceRequest.req_id,
            User.user_name,
            User.contact,
            User.address,
            User.pincode,
            ServiceRequest.status
        )
        .join(User, ServiceRequest.user_id == User.user_id)
        .filter(ServiceRequest.prof_id == prof_id, ServiceRequest.status == 'Requested')
        .all()
    )

        # Fetch today's requested services (status: 'Accepted')
    accept = (
        db.session.query(
            ServiceRequest.req_id,
            Service.name,
            User.user_name,
            User.contact,
            User.address,
            User.pincode,
            ServiceRequest.status
        )
        .join(User, ServiceRequest.user_id == User.user_id)
        .filter(ServiceRequest.prof_id == prof_id, ServiceRequest.status == 'Accepted')
        .all()
    )

        # Fetch today's requested services (status: 'Rejected')
    reject = (
        db.session.query(
            ServiceRequest.req_id,
            User.user_name,
            Service.name,
            User.contact,
            User.address,
            User.pincode,
            ServiceRequest.status
        )
        .join(User, ServiceRequest.user_id == User.user_id)
        .filter(ServiceRequest.prof_id == prof_id, ServiceRequest.status == 'Rejected')
        .all()
    )

    # Fetch closed services (status: 'Closed')
    closed_services = (
        db.session.query(
            ServiceRequest.req_id,
            User.user_name,
            Service.name,
            User.contact,
            User.address,
            User.pincode,
            ServiceRequest.close_date,
            ServiceRequest.status,
            ServiceRequest.rating,
            ServiceRequest.remarks
        )
        .join(User, ServiceRequest.user_id == User.user_id)
        .filter(ServiceRequest.prof_id == prof_id, ServiceRequest.status == 'Closed')
        .all()
    )


    # Render the template with retrieved data
    return render_template(
        'service_panel/professional_dashboard.html',
        today_services=today_services,
        closed_services=closed_services,
        services=services,
        accept=accept,
        reject=reject
    )




@main.route('/admin_dashboard')
def admin_dashboard():
     return redirect(url_for('admin.home'))
