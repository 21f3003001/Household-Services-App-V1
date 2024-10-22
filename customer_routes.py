from flask import Blueprint, render_template, redirect, url_for, session, request
from models import Service, ServiceRequest, db

customer_bp = Blueprint('customer', __name__)

# Customer dashboard
@customer_bp.route('/customer/dashboard')
def customer_dashboard():
    if session.get('role') == 'customer':
        services = Service.query.all()
        return render_template('customer_dashboard.html', services=services)
    return redirect(url_for('main.login'))

# Create a service request
@customer_bp.route('/customer/request/new/<int:service_id>', methods=['GET', 'POST'])
def create_service_request(service_id):
    if session.get('role') == 'customer':
        if request.method == 'POST':
            remarks = request.form['remarks']
            new_request = ServiceRequest(
                service_id=service_id,
                customer_id=session['user_id'],
                status='requested',
                remarks=remarks
            )
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('customer.customer_dashboard'))
        service = Service.query.get(service_id)
        return render_template('service_request_form.html', service=service)
    return redirect(url_for('main.login'))

# Post review for a service
@customer_bp.route('/customer/request/review/<int:request_id>', methods=['POST'])
def post_review(request_id):
    if session.get('role') == 'customer':
        service_request = ServiceRequest.query.get(request_id)
        service_request.review = request.form['review']
        db.session.commit()
        return redirect(url_for('customer.customer_dashboard'))
