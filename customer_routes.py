from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import db, Service, ServiceRequest, ServiceProfessional, User # Import necessary models
from datetime import datetime
from flask_login import login_required, current_user


customer_bp = Blueprint('customer', __name__)

# Route for viewing the customer dashboard
@customer_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must log in to access the dashboard.', 'danger')
        return redirect(url_for('main.login'))  # Replace with your login route

    # Fetch service history for the current user
    service_history = ServiceRequest.query.filter_by(user_id=user_id).all()

    # Query all available services
    services = Service.query.all()

    return render_template(
        'user_panel/customer_dashboard.html',
        services=services,
        service_history=service_history
    )


# Route for closing a service request
@customer_bp.route('/service_feedback/<int:request_id>', methods=['GET', 'POST'])
def service_feedback(request_id):
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to provide feedback.', 'danger')
        return redirect(url_for('main.login'))  # Replace 'main.login' with your login route

    # Fetch the service request
    service_request = ServiceRequest.query.get_or_404(request_id)

    # Ensure that the logged-in user owns the service request
    if service_request.user_id != user_id:
        flash('You cannot provide feedback for this service request.', 'danger')
        return redirect(url_for('customer.dashboard'))

    if request.method == 'POST':
        # Get form data
        rating = request.form.get('rating')
        remarks = request.form.get('remarks')

        # Validate rating
        if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
            flash('Invalid rating. Please select a valid rating between 1 and 5.', 'danger')
            return redirect(url_for('customer.service_feedback', request_id=request_id))

        # Update the service request with feedback
        service_request.rating = int(rating)
        service_request.remarks = remarks
        service_request.status = 'Closed'  # Update status to "Closed"
        service_request.close_date = datetime.now()  # Record closure date
        db.session.commit()

        flash('Your feedback has been submitted successfully!', 'success')
        return redirect(url_for('customer.dashboard'))

    # Render the feedback form
    return render_template(
        'user_panel/service_feedback.html',
        service_request=service_request
    )



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
        return redirect(url_for('main.login'))  # Redirect to login page

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



#Search

@customer_bp.route('/search', methods=['GET'])
def search():
    search_by = request.args.get('search_by')
    query = request.args.get('query', '').strip().lower()
    services = Service.query.all()

    # Get the logged-in user's ID
    user_id = session.get('user_id')  # Assuming `user_id` is stored in the session

    if not user_id:
        flash("Please log in to view your data.", "danger")
        return redirect(url_for('customer.login'))

    if search_by == "services":
        # Search for services the customer has requested
        results = (
            db.session.query(ServiceRequest)
            .join(Service, ServiceRequest.service_id == Service.id)
            .filter(
                ServiceRequest.user_id == user_id,  # Restrict to logged-in user
                Service.name.contains(query)
            )
            .all()
        )
    elif search_by == "professionals":
        # Search for professionals associated with services the customer has requested
        results = (
            db.session.query(ServiceProfessional)
            .join(ServiceRequest, ServiceRequest.prof_id == ServiceProfessional.prof_id)
            .filter(
                ServiceRequest.user_id == user_id,  # Restrict to logged-in user
                ServiceProfessional.prof_name.contains(query)
            )
            .all()
        )
    elif search_by == "requests":
        # Search for service requests by their status
        results = (
            ServiceRequest.query
            .filter(
                ServiceRequest.user_id == user_id,  # Restrict to logged-in user
                ServiceRequest.status.contains(query)
            )
            .all()
        )
    else:
        results = []

    # Pass results and query back to the template
    return render_template(
        'user_panel/search.html',
        results=results,
        search_by=search_by,
        query=query,
        services=services
    )


@customer_bp.route('/summary')
def summary():
    return render_template('user_panel/summary.html')

@customer_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')  # Fetch logged-in user's ID from the session
    if not user_id:
        flash("You must be logged in to update your profile.", "danger")
        return redirect(url_for('main.login'))  # Redirect to login if not logged in

    user = User.query.get_or_404(user_id)  # Fetch the user's details

    if request.method == 'POST':
        # Update the user's profile details
        user.username = request.form['username']
        user.user_name = request.form['user_name']
        user.address = request.form['address']
        user.contact = request.form['contact']
        user.pincode = request.form['pincode']

        # Update the password only if provided
        if request.form['password']:
            user.password = request.form['password']  # Add proper password hashing!

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.customer_dashboard'))

    return render_template('user_panel/profile.html', user=user)



def get_subcategories_for_service(service):
    # Placeholder function to retrieve subcategories based on service
    # Replace this with actual database query or logic
    service_map = {
        'cleaning': ["General house cleaning", "Deep cleaning", "Carpet cleaning", "Window cleaning"],
        'plumbing': ["Leak repairs", "Pipe installation", "Drain cleaning", "Water heater repair"],
        
    }
    return service_map.get(service, [])
