from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models import db, Service, ServiceProfessional, ServiceRequest, User
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/professional_dashboard/profile', methods=['GET', 'POST'])
def profile():
    # Fetch logged-in professional's ID from session
    prof_id = session.get('prof_id')
    if not prof_id:
        flash("You must be logged in to access your profile.", "danger")
        return redirect(url_for('main.login'))

    # Fetch the professional's details from the database
    professional = ServiceProfessional.query.get_or_404(prof_id)

    if request.method == 'POST':
        # Update profile fields
        professional.username = request.form['username']
        professional.prof_name = request.form['prof_name']
        professional.service_type = request.form['service_type']
        professional.experience = request.form['experience']
        professional.address = request.form['address']
        professional.contact = request.form['contact']
        professional.pincode = request.form['pincode']

        # Update the password if provided
        if request.form['password']:
            professional.password = generate_password_hash(request.form['password'])  # Use password hashing

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.professional_dashboard'))

    return render_template('service_panel/profile.html', professional=professional)



# Route to accept a service request
@professional_bp.route('/accept/<int:service_id>', methods=['GET'])
def accept_service(service_id):
    # Fetch the service request
    service_request = ServiceRequest.query.get_or_404(service_id)

    # Verify if the logged-in professional is assigned to this service
    professional_id = session.get('prof_id')  # Correct session key for professionals
    if service_request.prof_id != professional_id:  # Ensure it matches the logged-in professional
        flash("You cannot accept this service request.", "danger")
        return redirect(url_for('main.professional_dashboard'))

    # Update the status to 'Accepted' for the specific service request
    service_request.status = 'Accepted'
    db.session.commit()

    flash("Service request accepted successfully!", "success")
    return redirect(url_for('main.professional_dashboard'))


# Route to reject a service request
@professional_bp.route('/reject/<int:service_id>', methods=['GET'])
def reject_service(service_id):
    # Fetch the service request
    service_request = ServiceRequest.query.get_or_404(service_id)

    # Verify if the logged-in professional is assigned to this service
    professional_id = session.get('prof_id')  # Correct session key for professionals
    if service_request.prof_id != professional_id:  # Ensure it matches the logged-in professional
        flash("You cannot reject this service request.", "danger")
        return redirect(url_for('main.professional_dashboard'))

    # Update the status to 'Rejected' for the specific service request
    service_request.status = 'Rejected'
    db.session.commit()

    flash("Service request rejected successfully!", "success")
    return redirect(url_for('main.professional_dashboard'))


# Search functionality route
@professional_bp.route('/professional_dashboard/search', methods=['GET'])
def search():
    search_by = request.args.get('search_by')
    query = request.args.get('query', '').strip().lower()
    services = Service.query.all()

    # Get the logged-in professional's ID
    prof_id = session.get('prof_id')  # Assuming `prof_id` is stored in the session

    if not prof_id:
        flash("Please log in to view your data.", "danger")
        return redirect(url_for('customer.login'))

    if search_by == "customers":
        # Search for customers associated with the logged-in professional's service requests
        results = (
            db.session.query(
                ServiceRequest.req_id,
                Service.name,
                User.user_name,
                User.contact,
                User.address,
                User.pincode,
                ServiceRequest.close_date,
                ServiceRequest.status,
            )
            .join(ServiceRequest, ServiceRequest.user_id == User.user_id)
            .filter(
                ServiceRequest.prof_id == prof_id,  # Restrict to logged-in professional
                db.or_(
                    Service.name.contains(query),  # Search by service name
                    User.user_name.contains(query),  # Search by customer name
                    User.address.contains(query),  # Search by location
                    User.pincode.contains(query),  # Search by pincode
                    ServiceRequest.status.contains(query)  # Search by status
                )
            )
            .all()
        )
    elif search_by == "requests":
        # Search for service requests by multiple filters and fetch additional details
        results = (
            db.session.query(
                ServiceRequest.req_id,
                Service.name,
                User.user_name,
                User.contact,
                User.address,
                User.pincode,
                ServiceRequest.close_date,
                ServiceRequest.status,
                ServiceRequest.rating,
            )
            .join(User, ServiceRequest.user_id == User.user_id)  # Join with User table
            .join(Service, ServiceRequest.service_id == Service.service_id)  # Join with Service table
            .filter(
                ServiceRequest.prof_id == prof_id,  # Restrict to logged-in professional
                db.or_(
                    Service.name.contains(query),  # Search by service name
                    User.user_name.contains(query),  # Search by customer name
                    User.address.contains(query),  # Search by location
                    User.pincode.contains(query),  # Search by pincode
                    ServiceRequest.status.contains(query)  # Search by status
                )
            )
            .all()
        )
    else:
        results = []

    # Pass results and query back to the template
    return render_template(
        'service_panel/search.html',
        results=results,
        search_by=search_by,
        query=query,
        services=services
    )

@professional_bp.route('/professional_dashboard/summary', methods=['GET'])
def summary():
    return render_template('service_panel/summary.html')



