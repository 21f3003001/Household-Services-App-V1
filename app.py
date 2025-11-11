from flask import Flask
from routes import main
from admin_routes import admin_bp
from models import db, User
from werkzeug.security import generate_password_hash
from professional_routes import professional_bp
from customer_routes import customer_bp
from auth_routes import auth_bp
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Set the login view (redirect to login page if the user is not authenticated)
login_manager.login_view = 'auth.login'  # Update 'auth.login' to your actual login route

# User loader callback to get the user object based on user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)


# Create or overwrite the admin user
# Create or overwrite the admin user
# with app.app_context():
#     db.create_all()  # Ensure tables are created

#     # Check for existing admin user
#     admin_user = User.query.filter_by(username='admin').first()
#     if admin_user:
#         # If the admin user exists, update the password and role
#         hashed_password = generate_password_hash('admin1234', method='pbkdf2:sha256')
#         admin_user.password = hashed_password
#         admin_user.role = 'admin'
#         print("Admin user already exists. Password updated.")
#     else:
#         # If no admin user exists, create a new one with all required fields
#         hashed_password = generate_password_hash('admin1234', method='pbkdf2:sha256')
#         admin_user = User(
#             username='admin',
#             password=hashed_password,
#             name='Admin User',  # Set a valid name
#             address='123 Admin Street',  # Set a default address
#             contact='1234567890',  # Set a default contact
#             pincode='000000',  # Set a default pincode
#             role='admin'
#         )
#         db.session.add(admin_user)
#         print("Admin user created. Username: admin, Password: your_admin_password")

#     # Commit the changes
#     db.session.commit()



#Register the blueprint
app.register_blueprint(main)
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(auth_bp)
app.register_blueprint(professional_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True, host='0.0.0.0')



