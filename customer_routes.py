from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import db, Service, ServiceRequest, ServiceProfessional # Import necessary models
from datetime import datetime
from flask_login import login_required, current_user


customer_bp = Blueprint('customer', __name__)

# Route for viewing the customer dashboard
@customer_bp.route('/dashboard')
def dashboard():
    # Assuming 'current_user' is the logged-in customer
    user_id = current_user.user_id
    
    # Fetching service history for the current user (customer)
    service_history = ServiceRequest.query.filter_by(user_id=user_id).all()
    
    # Query all available services
    services = Service.query.all()

    return render_template(
        'user_panel/customer_dashboard.html',
        services=services,
        service_history=service_history
    )




# # Route for booking a service
# @customer_bp.route('/book_service/<int:service_id>', methods=['GET', 'POST'])
# def book_service(service_id):
#     user_id = session.get('user_id')  # Get user_id from the session

#     if not user_id:
#         flash('User not logged in. Please log in to book a service.', 'danger')
#         return redirect(url_for('main.customer_dashboard'))  # Redirect to home page if no user_id

#     service = Service.query.get_or_404(service_id)

#     # Check if the user has already booked this service
#     existing_request = ServiceRequest.query.filter_by(user_id=user_id, service_id=service_id, status='Requested').first()
#     if existing_request:
#         flash('You have already requested this service.', 'warning')
#         return redirect(url_for('customer.dashboard'))

#     # Handle the booking form
#     if request.method == 'POST':
#         new_request = ServiceRequest(
#             user_id=user_id,
#             service_id=service_id,
#             prof_id=None,  # Set based on your business logic
#             status='Requested',
#             requested_date=datetime.now()
#         )
#         db.session.add(new_request)
#         db.session.commit()

#         flash(f'Your {service.name} service has been successfully requested!', 'success')
#         return redirect(url_for('customer.dashboard'))

#     return render_template('user_panel/subcategory.html', service=service)


# Route for closing a service request
@customer_bp.route('/close_service/<int:request_id>', methods=['POST'])
def close_service(request_id):
    customer_id = request.args.get('customer_id')  # Get customer_id from the request

    if not customer_id:
        flash('Customer ID is required to close a service request.', 'danger')
        return redirect(url_for('main.index'))  # Redirect to home page or login page if no customer_id

    service_request = ServiceRequest.query.get_or_404(request_id)

    # Ensure that only the customer who made the request can close it
    if service_request.customer_id != customer_id:
        flash('You cannot close this service request.', 'danger')
        return redirect(url_for('customer.dashboard', customer_id=customer_id))

    # Check if the service request is still "Requested"
    if service_request.status != 'Requested':
        flash('This service request is already closed or completed.', 'warning')
        return redirect(url_for('customer.dashboard', customer_id=customer_id))

    # Update the status to "Closed"
    service_request.status = 'Closed'
    service_request.close_date = datetime.now()  # Optional: record the time of closure
    db.session.commit()

    flash(f'Your service request has been closed.', 'success')
    return redirect(url_for('customer.dashboard', customer_id=customer_id))


# Route for reviewing a service request
@customer_bp.route('/review_service/<int:request_id>', methods=['GET', 'POST'])
def review_service(request_id):
    customer_id = request.args.get('customer_id')  # Get customer_id from the request

    if not customer_id:
        flash('Customer ID is required to review a service.', 'danger')
        return redirect(url_for('main.index'))  # Redirect to home page or login page if no customer_id

    service_request = ServiceRequest.query.get_or_404(request_id)

    # Ensure that only the customer who made the request can review it
    if service_request.customer_id != customer_id:
        flash('You cannot review this service request.', 'danger')
        return redirect(url_for('customer.dashboard', customer_id=customer_id))

    # Check if the service request has been completed or closed
    if service_request.status != 'Closed':
        flash('You can only review closed services.', 'warning')
        return redirect(url_for('customer.dashboard', customer_id=customer_id))

    # Handle the review form submission
    if request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')

        # Add the review and rating to the service request
        service_request.rating = rating
        service_request.review = review
        db.session.commit()

        flash('Your review has been submitted successfully!', 'success')
        return redirect(url_for('customer.dashboard', customer_id=customer_id))

    return render_template('user_panel/review_service.html', service_request=service_request)



#Sub-Category

@customer_bp.route('/subcategory/<int:service_id>', methods=['GET'])
def subcategory(service_id):
    # Fetch the selected service
    service = Service.query.get(service_id)
    if not service:
        flash("Service not found!", "error")
        return redirect(url_for('customer.dashboard'))

    user_id = session.get('user_id')  # Get logged-in user's ID
    if not user_id:
        flash("You need to log in to access this page.", "danger")
        return redirect(url_for('auth.login'))  # Redirect to login page

    if request.args.get('action') == 'book_service':
        prof_id = None  # Initialize prof_id to None

        # Check if the service has already been requested by the user
        existing_request = ServiceRequest.query.filter_by(service_id=service_id, user_id=user_id, status='Requested').first()
        if existing_request:
            flash('This service has already been requested.', 'warning')
            return redirect(url_for('customer.subcategory', service_id=service_id))

        # Fetch a professional dynamically (adjust this query as needed)
        professional = ServiceProfessional.query.filter_by(service_type=service.name).first()  # Ensure 'service.name' exists in both models
        if professional:
            prof_id = professional.prof_id

        # Create a new service request
        new_request = ServiceRequest(
            service_id=service_id,
            user_id=user_id,
            prof_id=prof_id,  # Assign the selected professional ID
            status='Requested',
            requested_date=datetime.utcnow()
        )
        try:
            db.session.add(new_request)
            db.session.commit()
            flash(f'The {service.name} service has been successfully requested!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error requesting the service: {str(e)}', 'danger')

        # Stay on the same subcategory page after booking
        return redirect(url_for('customer.subcategory', service_id=service_id))

    # Fetch related services and service history
    services = Service.query.filter(Service.service_id == service_id).all()
    service_history = ServiceRequest.query.filter_by(service_id=service_id, user_id=user_id).all()

    return render_template(
        'user_panel/subcategory.html',
        service=service,
        services=services,
        service_history=service_history
    )




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

# @customer_bp.route('/book_service/<int:service_id>', methods=['POST'])
# def book_service(service_id):
#     # Book the selected service
#     new_request = ServiceRequest(service_id=service_id, status='Requested', request_date=datetime.now())
#     db.session.add(new_request)
#     db.session.commit()
#     flash("Service booked successfully.")
#     return redirect(url_for('customer.dashboard'))

# @customer_bp.route('/close_service/<int:request_id>', methods=['POST'])
# def close_service(request_id):
#     # Update the service status to closed
#     service_request = ServiceRequest.query.get(request_id)
#     service_request.status = 'Closed'
#     db.session.commit()
#     flash("Service closed successfully.")
#     return redirect(url_for('customer.dashboard'))

# @customer_bp.route('/review_service/<int:request_id>', methods=['GET', 'POST'])
# def review_service(request_id):
#     if request.method == 'POST':
#         # Save the review
#         rating = request.form.get('rating')
#         remarks = request.form.get('remarks')
#         service_request = ServiceRequest.query.get(request_id)
#         service_request.rating = rating
#         service_request.remarks = remarks
#         db.session.commit()
#         flash("Thank you for your feedback!")
#         return redirect(url_for('customer.dashboard'))
#     return render_template('user_panel/review.html', request_id=request_id)







def get_subcategories_for_service(service):
    # Placeholder function to retrieve subcategories based on service
    # Replace this with actual database query or logic
    service_map = {
        'cleaning': ["General house cleaning", "Deep cleaning", "Carpet cleaning", "Window cleaning"],
        'plumbing': ["Leak repairs", "Pipe installation", "Drain cleaning", "Water heater repair"],
        
    }
    return service_map.get(service, [])
