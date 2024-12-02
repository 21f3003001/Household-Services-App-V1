from flask import Blueprint, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/logout')
def logout():
    # Logic to log out the user, e.g., clearing the session
    session.clear()
    return redirect(url_for('main.login'))


