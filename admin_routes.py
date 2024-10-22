from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from models import Service, ServiceProfessional, Customer, db

admin_bp = Blueprint('admin', __name__)

# Admin dashboard
@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') == 'admin':
        services = Service.query.all()
        professionals = ServiceProfessional.query.all()
        customers = Customer.query.all()
        return render_template('admin_dashboard.html', services=services, professionals=professionals, customers=customers)
    return redirect(url_for('main.login'))

# Create a new service
@admin_bp.route('/admin/service/new', methods=['GET', 'POST'])
def create_service():
    if session.get('role') == 'admin':
        if request.method == 'POST':
            service_name = request.form['service_name']
            base_price = request.form['base_price']
            description = request.form['description']
            new_service = Service(name=service_name, price=base_price, description=description)
            db.session.add(new_service)
            db.session.commit()
            flash("Service created successfully!", "success")
            return redirect(url_for('admin.admin_dashboard'))
        return render_template('service_form.html')
    return redirect(url_for('main.login'))

# Approve professionals
@admin_bp.route('/admin/professional/approve/<int:professional_id>', methods=['POST'])
def approve_professional(professional_id):
    if session.get('role') == 'admin':
        professional = ServiceProfessional.query.get(professional_id)
        professional.is_approved = True
        db.session.commit()
        flash("Professional approved!", "success")
        return redirect(url_for('admin.admin_dashboard'))

# Block customer or professional
@admin_bp.route('/admin/block/<string:user_type>/<int:user_id>', methods=['POST'])
def block_user(user_type, user_id):
    if session.get('role') == 'admin':
        if user_type == 'customer':
            user = Customer.query.get(user_id)
        elif user_type == 'professional':
            user = ServiceProfessional.query.get(user_id)
        user.is_blocked = True
        db.session.commit()
        flash(f"{user_type.capitalize()} blocked successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))
