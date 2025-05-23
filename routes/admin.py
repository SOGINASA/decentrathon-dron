from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_models import Admin, db, User, Drone


admin_bp = Blueprint('admin', __name__)

def drone_map():
    if current_user.is_authenticated:
        if session.get('is_admin'):
            drones = Drone.query.all()
            return render_template('drone_map.html', drones=drones)
    return redirect('/auth/login')

def register_drone():
    pass

def admin_dashboard():
    if current_user.is_authenticated:
        if session.get('is_admin'):
            return render_template('main.html')
        else:
            return redirect('/user/dashboard')
    return redirect('/auth/login')

admin_bp.add_url_rule('/drone_map',view_func=drone_map ,methods=['GET', 'POST'])
admin_bp.add_url_rule('/register_drone', view_func=register_drone,methods=['GET', 'POST'])
admin_bp.add_url_rule('/dashboard', view_func=admin_dashboard, methods=['GET'])