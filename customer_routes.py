from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, Service  # Import necessary models
from datetime import datetime
from flask_login import current_user


customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/dashboard')
def dashboard():
    # Ensure the user is authenticated before accessing their ID
    if not current_user.is_authenticated:
        return redirect(url_for('main.customer_dashboard'))  # Replace 'auth.login' with the actual route to your login page
    
    service_history = ServiceRequest.query.filter_by(customer_id=current_user.id).all()  # Service history for logged-in user
    return render_template('customer_dashboard.html', service_history=service_history)

@customer_bp.route('/search')
def search():
    return render_template('user_panel/search_service.html')

@customer_bp.route('/summary')
def summary():
    return render_template('user_panel/summary.html')

@customer_bp.route('/profile')
def profile():
    # Logic for rendering the profile page
    return render_template('user_panel/profile.html')

@customer_bp.route('/book_service/<int:service_id>', methods=['POST'])
def book_service(service_id):
    # Book the selected service
    new_request = ServiceRequest(customer_id=current_user.id, service_id=service_id, status='Requested', request_date=datetime.now())
    db.session.add(new_request)
    db.session.commit()
    flash("Service booked successfully.")
    return redirect(url_for('customer.dashboard'))

@customer_bp.route('/close_service/<int:request_id>', methods=['POST'])
def close_service(request_id):
    # Update the service status to closed
    service_request = ServiceRequest.query.get(request_id)
    service_request.status = 'Closed'
    db.session.commit()
    flash("Service closed successfully.")
    return redirect(url_for('customer.dashboard'))

@customer_bp.route('/review_service/<int:request_id>', methods=['GET', 'POST'])
def review_service(request_id):
    if request.method == 'POST':
        # Save the review
        rating = request.form.get('rating')
        remarks = request.form.get('remarks')
        service_request = ServiceRequest.query.get(request_id)
        service_request.rating = rating
        service_request.remarks = remarks
        db.session.commit()
        flash("Thank you for your feedback!")
        return redirect(url_for('customer.dashboard'))
    return render_template('user_panel/review.html', request_id=request_id)


#Sub_category

@customer_bp.route('/subcategory/<service>', methods=['GET'])
def subcategory(service):
    # Fetch service details based on service_id
    main_service = Service.query.get(service)
    #sub_services = SubService.query.filter_by(service=service).all()
    
    # Render the subcategory page, passing service_name and sub_services
    return render_template('user_panel/subcategory.html', service=service)


def get_subcategories_for_service(service):
    # Placeholder function to retrieve subcategories based on service
    # Replace this with actual database query or logic
    service_map = {
        'cleaning': ["General house cleaning", "Deep cleaning", "Carpet cleaning", "Window cleaning"],
        'plumbing': ["Leak repairs", "Pipe installation", "Drain cleaning", "Water heater repair"],
        
    }
    return service_map.get(service, [])
