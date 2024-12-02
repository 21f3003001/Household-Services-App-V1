from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import db, Service, ServiceProfessional, ServiceRequest

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/professional_dashboard')
def professional_dashboard():
    # Ensure user is logged in and is a Service Professional
    if 'user_id' not in session or session.get('role') != 'service_professional':
        flash('Please log in as a Service Professional.', 'danger')
        return redirect(url_for('main.login'))

    # Fetch the logged-in professional's data
    professional_id = session['user_id']
    today_services = ServiceRequest.query.filter_by(professional_id=professional_id, status='pending').all()
    closed_services = ServiceRequest.query.filter_by(professional_id=professional_id, status='closed').all()

    return render_template(
        'service_panel/professional_dashboard.html',
        today_services=today_services,
        closed_services=closed_services
    )


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