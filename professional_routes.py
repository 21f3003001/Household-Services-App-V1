from flask import Blueprint, render_template, redirect, url_for, session, request
from models import ServiceRequest, db

professional_bp = Blueprint('professional', __name__)

# Professional dashboard
@professional_bp.route('/professional/dashboard')
def professional_dashboard():
    if session.get('role') == 'professional':
        professional_id = session['user_id']
        service_requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()
        return render_template('professional_dashboard.html', service_requests=service_requests)
    return redirect(url_for('main.login'))

# Accept or reject a service request
@professional_bp.route('/professional/request/<int:request_id>/<string:action>', methods=['POST'])
def handle_request(request_id, action):
    if session.get('role') == 'professional':
        service_request = ServiceRequest.query.get(request_id)
        if action == 'accept':
            service_request.status = 'accepted'
        elif action == 'reject':
            service_request.status = 'rejected'
        db.session.commit()
        return redirect(url_for('professional.professional_dashboard'))
