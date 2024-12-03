from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models import db, Service, ServiceProfessional, ServiceRequest, User
from datetime import datetime

professional_bp = Blueprint('professional', __name__)

# @professional_bp.route('/professional_dashboard', methods=['GET'])
# def professional_dashboard():
#     # Fetch logged-in professional's ID from session
#     prof_id = session.get('prof_id')
#     if not prof_id:
#         flash("You must be logged in to view your dashboard.", "danger")
#         return redirect(url_for('main.login'))  # Redirect to login page if not logged in

#     # Fetch today's requested services (status: 'Requested')
#     today_services = (
#         db.session.query(
#             ServiceRequest.req_id,
#             User.user_name,
#             User.contact,
#             User.address,
#             User.pincode,
#             ServiceRequest.status
#         )
#         .join(User, ServiceRequest.user_id == User.user_id)
#         .filter(ServiceRequest.prof_id == prof_id, ServiceRequest.status == 'Requested')
#         .all()
#     )

#     # Fetch closed services (status: 'Closed')
#     closed_services = (
#         db.session.query(
#             ServiceRequest.req_id,
#             User.user_name,
#             User.contact,
#             User.address,
#             User.pincode,
#             ServiceRequest.close_date,
#             ServiceRequest.rating,
#             ServiceRequest.remarks
#         )
#         .join(User, ServiceRequest.user_id == User.user_id)
#         .filter(ServiceRequest.prof_id == prof_id, ServiceRequest.status == 'Closed')
#         .all()
#     )

#     # Debugging output to verify query results
#     print("Today's Services:", today_services)
#     print("Closed Services:", closed_services)

#     # Render the template with retrieved data
#     return render_template(
#         'service_panel/professional_dashboard.html',
#         today_services=today_services,
#         closed_services=closed_services
#     )




# Route to accept a service request
@professional_bp.route('/accept/<int:service_id>', methods=['GET'])
def accept_service(service_id):
    # Fetch the service request
    service_request = ServiceRequest.query.get_or_404(service_id)

    # Verify if the logged-in professional is assigned to this service
    professional_id = session.get('prof_id')  # Correct session key for professionals
    if service_request.prof_id != professional_id:  # Ensure this field matches the model's actual column name
        flash("You cannot accept this service request.", "danger")
        return redirect(url_for('professional.professional_dashboard'))

    # Update the status to 'Accepted'
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
    if service_request.prof_id != professional_id:  # Ensure this field matches the model's actual column name
        flash("You cannot reject this service request.", "danger")
        return redirect(url_for('professional.professional_dashboard'))

    # Update the status to 'Rejected'
    service_request.status = 'Rejected'
    db.session.commit()

    flash("Service request rejected successfully!", "success")
    return redirect(url_for('main.professional_dashboard'))



# Search functionality route
@professional_bp.route('/professional_dashboard/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    # Add search logic here (e.g., filter services, professionals, or service requests based on the query)
    # For now, just render the search page (implement search logic as needed)
    return render_template('service_panel/search.html', query=query)

@professional_bp.route('/professional_dashboard/summary', methods=['GET'])
def summary():
    return render_template('service_panel/summary.html')

@professional_bp.route('/professional_dashboard/profile')
def profile():
    # Logic for rendering the profile page
    return render_template('service_panel/profile.html')

from flask import jsonify, request  # Ensure both are imported

@professional_bp.route('/test_query', methods=['GET'])
def test_query():
    # Fetch logged-in professional's ID from session
    prof_id = session.get('prof_id')
    if not prof_id:
        return jsonify({"error": "Professional ID not found in session"}), 401

    # Fetch service request based on req_id for the logged-in professional
    req_id = session.get('req_id')
    if not req_id:
        return jsonify({"error": "Request ID is required"}), 400

    # Query the database
    service_request = ServiceRequest.query.filter_by(req_id=req_id, prof_id=prof_id).first()

    # Debug output
    if not service_request:
        return jsonify({"error": "No service request found with the provided req_id"}), 404

    # Show raw database result for debugging
    return jsonify({
        "req_id": service_request.req_id,
        "user_id": service_request.user_id,
        "service_id": service_request.service_id,
        "prof_id": service_request.prof_id,
        "status": service_request.status,
        "rating": service_request.rating,
        "remarks": service_request.remarks,
        "requested_date": service_request.requested_date.isoformat(),
        "close_date": service_request.close_date.isoformat()
    })


