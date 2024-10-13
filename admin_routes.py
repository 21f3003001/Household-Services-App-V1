from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Service
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

# Admin: Admin Dashboard
@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') == 'admin':
        services = Service.query.all()
        professionals = User.query.filter_by(role='professional').all()
        customers = User.query.filter_by(role='customer').all()
        return render_template('admin_panel/admin_dashboard.html', services=services, professionals=professionals, customers=customers)
    return redirect(url_for('main.login'))

# Admin: Add a new service professional
@admin_bp.route('/admin/professional/new', methods=['GET', 'POST'])
def add_professional():
    if session.get('role') == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Hash the password for security
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_professional = User(username=username, password=hashed_password, role='professional')

            db.session.add(new_professional)
            db.session.commit()
            flash("Service Professional added successfully!", "success")
            return redirect(url_for('admin.admin_dashboard'))  # Updated to match blueprint name
        
        return render_template('admin_panel/add_professional.html')

# Admin: Add a new customer
@admin_bp.route('/admin/customer/new', methods=['GET', 'POST'])
def add_customer():
    if session.get('role') == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Hash the password for security
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_customer = User(username=username, password=hashed_password, role='customer')

            db.session.add(new_customer)
            db.session.commit()
            flash("Customer added successfully!", "success")
            return redirect(url_for('admin.admin_dashboard'))  # Updated to match blueprint name

        return render_template('admin_panel/add_customer.html')

# Admin: Remove service professional or customer
@admin_bp.route('/admin/professional/remove/<int:id>', methods=['POST'])
def remove_professional(id):
    if session.get('role') == 'admin':
        professional = User.query.get_or_404(id)
        db.session.delete(professional)
        db.session.commit()
        flash("Service Professional removed successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))  # Updated to match blueprint name

@admin_bp.route('/admin/customer/remove/<int:id>', methods=['POST'])
def remove_customer(id):
    if session.get('role') == 'admin':
        customer = User.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        flash("Customer removed successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))  # Updated to match blueprint name

