from models import db, Service, SubService
from app import create_app

# Initialize the Flask app
app = create_app()

# Run the app context to access the database
with app.app_context():
    # Create the services
    cleaning = Service(name="Cleaning Services")
    plumbing = Service(name="Plumbing Services")

    # Adding sub-services for Cleaning
    general_cleaning = SubService(name="General house cleaning", price=50.0, service=cleaning)
    deep_cleaning = SubService(name="Deep cleaning", price=100.0, service=cleaning)

    # Adding sub-services for Plumbing
    leak_repair = SubService(name="Leak repairs", price=75.0, service=plumbing)
    pipe_install = SubService(name="Pipe installation/replacement", price=120.0, service=plumbing)

    # Add services and sub-services to the session and commit them to the database
    db.session.add_all([cleaning, plumbing, general_cleaning, deep_cleaning, leak_repair, pipe_install])
    db.session.commit()

    print("Services and Sub-services added successfully!")
