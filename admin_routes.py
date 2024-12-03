import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, Service, ServiceProfessional, ServiceRequest, ProfessionalStatus, User

admin_bp = Blueprint('admin', __name__)

# Admin dashboard home
@admin_bp.route('/admin')
def home():
    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    service_requests = ServiceRequest.query.all()
    customers = User.query.all()
    return render_template('admin_panel/admin_dashboard.html', services=services, 
                           professionals=professionals, service_requests=service_requests, customers=customers)

# Add new service
# Configure allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/admin_dashboard/add_service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        # Extract form data
        dropdown_service_name = request.form.get('name')  # From dropdown
        custom_service_name = request.form.get('new_service_type')  # Custom service name
        description = request.form.get('description')  # Service description
        base_price = request.form.get('base_price')  # Base price

        # Determine the service name: custom input takes priority over dropdown
        name = custom_service_name.strip() if custom_service_name else dropdown_service_name

        # Validate inputs
        if not name:
            flash('Service name is required.', 'danger')
            return redirect(url_for('admin.add_service'))

        if not description:
            flash('Service description is required.', 'danger')
            return redirect(url_for('admin.add_service'))

        try:
            base_price = float(base_price)
            if base_price < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('Valid base price is required (non-negative number).', 'danger')
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
            name=name,  # Only the name attribute is used
            description=description,
            base_price=base_price,
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

    # Fetch all existing service names to populate dropdown
    services = Service.query.with_entities(Service.name).distinct().all()
    return render_template('admin_panel/add_service.html', services=services)




# Edit service
@admin_bp.route('/admin_dashboard/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        # Extract form data
        dropdown_service_name = request.form.get('name')  # From dropdown
        custom_service_name = request.form.get('new_service_type')  # Custom service name
        description = request.form.get('description')  # Service description
        base_price = request.form.get('base_price')  # Base price

        # Determine the service name: custom input takes priority over dropdown
        name = custom_service_name.strip() if custom_service_name else dropdown_service_name

        # Validate inputs
        if not name:
            flash('Service name is required.', 'danger')
            return redirect(url_for('admin.edit_service', service_id=service_id))

        if not description:
            flash('Service description is required.', 'danger')
            return redirect(url_for('admin.edit_service', service_id=service_id))

        try:
            base_price = float(base_price)
            if base_price < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('Valid base price is required (non-negative number).', 'danger')
            return redirect(url_for('admin.edit_service', service_id=service_id))

        # Handle image file upload
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            try:
                # Secure the filename and save the file
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)  # Create folder if it doesn't exist
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                service.image = f'static/uploads/{filename}'  # Update the service image
            except Exception as e:
                flash(f'Error saving the image: {str(e)}', 'danger')
                return redirect(url_for('admin.edit_service', service_id=service_id))
        elif file:
            flash('Invalid image file. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')
            return redirect(url_for('admin.edit_service', service_id=service_id))

        # Update service details in the database
        service.name = name
        service.description = description
        service.base_price = base_price

        try:
            db.session.commit()
            flash('Service updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating service: {str(e)}', 'danger')
        return redirect(url_for('admin.home'))

    # Fetch all existing service names to populate dropdown
    services = Service.query.with_entities(Service.name).distinct().all()
    return render_template('admin_panel/edit_service.html', service=service, services=services)



# Delete service
@admin_bp.route('/admin_dashboard/delete_service/<int:service_id>')
def delete_service(service_id):
    service = Service.query.get(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))


# Adding Professional in Admin Dashboard
@admin_bp.route('/admin_dashboard/add_professional', methods=['GET', 'POST'])
def add_professional():
    if request.method == 'POST':
        # Extract data from the form
        username = request.form.get('username')
        password = request.form.get('password')
        prof_name = request.form.get('prof_name')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')
        address = request.form.get('address')
        contact = request.form.get('contact')
        pincode = request.form.get('pincode')
        role = request.form.get('role', 'service_professional')

        # Validate form inputs
        if not all([username, password, prof_name, service_type, address, contact, pincode]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.add_professional'))

        # Check if the username already exists
        existing_professional = ServiceProfessional.query.filter_by(username=username).first()
        if existing_professional:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.add_professional'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new ServiceProfessional object
        new_professional = ServiceProfessional(
            username=username,
            password=hashed_password,
            prof_name=prof_name,
            service_type=service_type,
            experience=experience,
            address=address,
            contact=contact,
            pincode=pincode,
            date_created=datetime.utcnow(),
            role=role
        )

        try:
            # Add to the database
            db.session.add(new_professional)
            db.session.commit()
            flash('Professional added successfully!', 'success')
            return redirect(url_for('admin.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding professional: {str(e)}', 'danger')
            return redirect(url_for('admin.add_professional'))

    # Query all available services to display in the form
    services = Service.query.all()
    return render_template('admin_panel/add_professional.html', services=services)



# Adding Customer in Admin Dashboard
@admin_bp.route('/admin_dashboard/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        # Extract data from the form
        username = request.form.get('username')
        password = request.form.get('password')
        user_name = request.form.get('user_name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        pincode = request.form.get('pincode')
        role = request.form.get('role', 'customer')

        # Validate form inputs
        if not all([username, password, user_name, address, contact, pincode]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.add_customer'))

        # Check if the username already exists
        existing_customer = User.query.filter_by(username=username).first()
        if existing_customer:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.add_customer'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new ServiceProfessional object
        new_customer = User(
            username=username,
            password=hashed_password,
            user_name=user_name,
            address=address,
            contact=contact,
            pincode=pincode,
            date_created=datetime.utcnow(),
            role=role
        )

        try:
            # Add to the database
            db.session.add(new_customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('admin.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'danger')
            return redirect(url_for('admin.add_customer'))

    # Query all available services to display in the form
    services = Service.query.all()

    return render_template('admin_panel/add_customer.html', services=services)

# Block Customer
@admin_bp.route('/admin_dashboard/block_customer/<int:customer_id>', methods=['GET'])
def block_customer(customer_id):
    customer = User.query.get_or_404(customer_id)
    try:
        if customer.status == 'Blocked':
            flash('Customer is already blocked.', 'info')
        else:
            customer.status = 'Blocked'
            db.session.commit()
            flash('Customer blocked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error blocking customer: {str(e)}', 'danger')
    return redirect(url_for('admin.home'))


# Unblock Customer
@admin_bp.route('/admin_dashboard/unblock_customer/<int:customer_id>', methods=['GET'])
def unblock_customer(customer_id):
    customer = User.query.get_or_404(customer_id)
    try:
        if customer.status == 'Active':
            flash('Customer is already active.', 'info')
        else:
            customer.status = 'Active'
            db.session.commit()
            flash('Customer unblocked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error unblocking customer: {str(e)}', 'danger')
    return redirect(url_for('admin.home'))



@admin_bp.route('/approve_professional/<int:professional_id>')
def approve_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional:
        professional.status = ProfessionalStatus.APPROVED  
        db.session.commit()
        flash("Professional approved successfully!", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for('admin.home'))

@admin_bp.route('/reject_professional/<int:professional_id>')
def reject_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional:
        professional.status = ProfessionalStatus.REJECTED  
        db.session.commit()
        flash("Professional rejected successfully!", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for('admin.home'))


@admin_bp.route('/admin_dashboard/delete_professional/<int:professional_id>')
def delete_professional(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    try:
        db.session.delete(professional)
        db.session.commit()
        flash('Professional deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting professional: {str(e)}', 'danger')
    return redirect(url_for('admin.home'))

# Search functionality route
@admin_bp.route('/admin_dashboard/search', methods=['GET'])
def search():
    search_by = request.args.get('search_by')
    query = request.args.get('query', '').strip().lower()
    services = Service.query.all()

    if search_by == "services":
        # Filter by service name
        results = Service.query.filter(Service.name.contains(query)).all()

    elif search_by == "customers":
        # Filter by user name, location, pincode, or status
        results = (
            User.query.filter(
                db.or_(
                    User.user_name.contains(query),
                    User.address.contains(query),
                    User.pincode.contains(query),
                    User.status.contains(query),
                )
            ).all()
        )

    elif search_by == "professionals":
    # Filter by professional name, location, pincode, status, or service name
        results = (
            db.session.query(
                ServiceProfessional,
                Service.name.label("service_name")  # Select service name explicitly
            )
            .join(ServiceProfessional, Service.service_id == Service.service_id)  # Join with Service table
            .filter(
                db.or_(
                    ServiceProfessional.prof_name.contains(query),
                    ServiceProfessional.address.contains(query),
                    ServiceProfessional.pincode.contains(query),
                    ServiceProfessional.status.contains(query),
                    Service.name.contains(query),  # Filter by service name
                )
            )
            .all()
        )


    elif search_by == "requests":
        # Filter by professional name, status, or rating
        results = (
            db.session.query(
                ServiceRequest.req_id,
                ServiceProfessional.prof_name,
                ServiceRequest.requested_date,
                ServiceRequest.status,
                ServiceRequest.rating,
            )
            .join(ServiceProfessional, ServiceRequest.prof_id == ServiceProfessional.prof_id)
            .filter(
                db.or_(
                    ServiceProfessional.prof_name.contains(query),
                    ServiceRequest.status.contains(query),
                    ServiceRequest.rating.contains(query),
                )
            )
            .all()
        )

    else:
        results = []

    # Pass results and query back to the template
    return render_template(
        'admin_panel/search.html', 
        results=results, 
        search_by=search_by, 
        query=query, 
        services=services
    )


@admin_bp.route('/admin_dashboard/summary', methods=['GET'])
def summary():
    return render_template('admin_panel/summary.html')