from flask import Flask
from models import db
from routes import main  # Import the routes module

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
db.init_app(app)

# Register the Blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
