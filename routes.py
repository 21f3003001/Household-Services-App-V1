from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Service, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash


# Create a Blueprint for routes
main = Blueprint('main', __name__)

# User roles: Admin, Service Professional, Customer
roles = ['admin', 'professional', 'customer']


@main.route('/')
def index():
    return render_template('login.html')

# Registration Route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if the user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already taken. Please choose another.", "danger")
            return redirect(url_for('main.register'))

        # Hash the password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role=role)

        # Save the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Display success message without using flash
        return render_template('register.html', success_message="Registration successful! You can now log in.")
    
    return render_template('register.html')


# Login Route for Users (Admin/Professional/Customer)
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if user.role == role:
                session['user_id'] = user.id
                session['role'] = user.role

                if user.role == 'admin':
                    return redirect(url_for('main.admin_dashboard'))
                elif user.role == 'professional':
                    return redirect(url_for('main.professional_dashboard'))
                elif user.role == 'customer':
                    return redirect(url_for('main.customer_dashboard'))
            else:
                flash("Role mismatch. Please select the correct role.", "danger")
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template('login.html')


@main.route('/logout')
def logout():
    # Remove user session
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('main.login'))

# Admin Dashboard Route
@main.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') == 'admin':
        return render_template('admin_panel/admin_dashboard.html')
    return redirect(url_for('main.login'))

# Service Professional Dashboard
@main.route('/professional/dashboard')
def professional_dashboard():
    if session.get('role') == 'professional':
        requests = ServiceRequest.query.filter_by(professional_id=session['user_id']).all()
        return render_template('professional_dashboard.html', requests=requests)
    return redirect(url_for('main.login'))

# Customer Dashboard
@main.route('/customer/dashboard')
def customer_dashboard():
    if session.get('role') == 'customer':
        services = Service.query.all()
        return render_template('customer_dashboard.html', services=services)
    return redirect(url_for('main.login'))

# Admin: Create a new service
@main.route('/admin/service/new', methods=['GET', 'POST'])
def create_service():
    if session.get('role') == 'admin':
        if request.method == 'POST':
            service_name = request.form['service_name']
            base_price = request.form['base_price']
            new_service = Service(name=service_name, price=base_price)
            db.session.add(new_service)
            db.session.commit()
            return redirect(url_for('main.admin_dashboard'))
        return render_template('service_form.html')
    return redirect(url_for('main.login'))

# Customer: Create a service request
@main.route('/customer/request/new/<int:service_id>', methods=['GET', 'POST'])
def create_service_request(service_id):
    if session.get('role') == 'customer':
        if request.method == 'POST':
            new_request = ServiceRequest(
                service_id=service_id,
                customer_id=session['user_id'],
                status='requested',
                remarks=request.form['remarks']
            )
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('main.customer_dashboard'))
        service = Service.query.get(service_id)
        return render_template('service_form.html', service=service)
    return redirect(url_for('main.login'))
