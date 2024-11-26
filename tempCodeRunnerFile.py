# # Create or overwrite the admin user
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
#         # If no admin user exists, create a new one
#         hashed_password = generate_password_hash('admin1234', method='pbkdf2:sha256')
#         admin_user = User(username='admin', password=hashed_password, role='admin')
#         db.session.add(admin_user)
#         print("Admin user created. Username: admin, Password: your_admin_password")

#     # Commit the changes
#     db.session.commit()