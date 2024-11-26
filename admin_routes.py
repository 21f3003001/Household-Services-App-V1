import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
from models import db, Service, ServiceProfessional, ServiceRequest

admin_bp = Blueprint('admin', __name__)

# Admin dashboard home
@admin_bp.route('/admin')
def home():
    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    service_requests = ServiceRequest.query.all()
    return render_template('admin_panel/admin_dashboard.html', services=services, 
                           professionals=professionals, service_requests=service_requests)

# Add new service
# Configure allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add new service
@admin_bp.route('/admin_dashboard/add_service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        description = request.form.get('description')
        base_price = request.form.get('base_price')
        service_name = request.form.get('service_name')  # Supporting a simpler name field for compatibility

        # Validate inputs
        if not name:
            flash('Service name is required.', 'danger')
            return redirect(url_for('admin.add_service'))

        if not base_price or not base_price.isdigit() or float(base_price) < 0:
            flash('Valid base price is required.', 'danger')
            return redirect(url_for('admin.add_service'))

        # Handle image file upload
        image_path = None  # Default to no image
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            try:
                # Secure the filename and save the file
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)  # Create folder if it doesn't exist
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                image_path = f'static/uploads/{filename}'  # Save relative path for database
            except Exception as e:
                flash(f'Error saving the image: {str(e)}', 'danger')
                return redirect(url_for('admin.add_service'))
        elif file:
            flash('Invalid image file. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')
            return redirect(url_for('admin.add_service'))

        # Save service details to the database
        new_service = Service(
            name=name or service_name,
            description=description,
            base_price=float(base_price),
            image=image_path
        )

        try:
            db.session.add(new_service)
            db.session.commit()
            flash('Service added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding service: {str(e)}', 'danger')
        return redirect(url_for('admin.home'))

    # Fetch all available services to populate dropdowns or other data
    services = Service.query.all()
    return render_template('admin_panel/add_service.html', services=services)



# Edit service
@admin_bp.route('/admin_dashboard/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get(service_id)
    if request.method == 'POST':
        service.name = request.form['name']
        service.description = request.form['description']
        service.base_price = float(request.form['base_price'])
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin.home'))
    return render_template('admin_panel/edit_service.html', service=service)

# Delete service
@admin_bp.route('/admin_dashboard/delete_service/<int:service_id>')
def delete_service(service_id):
    service = Service.query.get(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

# Approve professional
@admin_bp.route('/admin_dashboard/approve_professional/<int:professional_id>')
def approve_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    professional.status = 'Approved'
    db.session.commit()
    flash('Professional approved successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

# Reject professional
@admin_bp.route('/admin_dashboard/reject_professional/<int:professional_id>')
def reject_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    professional.status = 'Rejected'
    db.session.commit()
    flash('Professional rejected successfully!', 'warning')
    return redirect(url_for('main.admin_dashboard'))

# Delete professional
@admin_bp.route('/admin_dashboard/delete_professional/<int:professional_id>')
def delete_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    db.session.delete(professional)
    db.session.commit()
    flash('Professional deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

# Route to add a new professional
@admin_bp.route('/admin_dashboard/add_professional', methods=['GET', 'POST'])
def add_professional():
    if request.method == 'POST':
        # Handle form submission logic here
        # Example: Fetch data from form and add a new professional to the database
        pass  # Replace with actual logic to add a professional
    return render_template('admin_panel/add_user/add_professional.html')  # Ensure this template exists


# Search functionality route
@admin_bp.route('/admin_dashboard/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    # Add search logic here (e.g., filter services, professionals, or service requests based on the query)
    # For now, just render the search page (implement search logic as needed)
    return render_template('admin_panel/search.html', query=query)

@admin_bp.route('/admin_dashboard/summary', methods=['GET'])
def summary():
    return render_template('admin_panel/summary.html')