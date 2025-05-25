from flask import redirect, render_template, request, session, Blueprint
from flask_login import current_user
from db_models import db, Drone, Log


admin_bp = Blueprint('admin', __name__)

def drones():
    if current_user.is_authenticated:
        if request.method == 'POST':
            mark = request.form.get('mark')
            model = request.form.get('model')
            serial = request.form.get('serial')
            lat = 0
            lng = 0
            new_drone = Drone(mark=mark, model=model, serial=serial, lat=lat, lng=lng)
            db.session.add(new_drone)
            db.session.commit()
        if session.get('is_admin'):
            drones = Drone.query.all()
            return render_template('drones.html', drones=drones)
    return redirect('/auth/login')



def admin_dashboard():
    if current_user.is_authenticated:
        if session.get('is_admin'):
            return render_template('main.html')
        else:
            return redirect('/user/dashboard')
    return redirect('/auth/login')

def logs():
    if not current_user.is_authenticated or not session.get('is_admin'):
        return redirect('/auth/login')
    logs = Log.query.all()
    return render_template('logs.html', logs=logs)

def missions():
    if not current_user.is_authenticated or not session.get('is_admin'):
        return redirect('/auth/login')
    return render_template('missions.html')

admin_bp.add_url_rule('/drones',view_func=drones ,methods=['GET', 'POST'])
admin_bp.add_url_rule('/dashboard', view_func=admin_dashboard, methods=['GET'])
admin_bp.add_url_rule('/logs', view_func=logs, methods=['GET'])
admin_bp.add_url_rule('/missions', view_func=missions, methods=['GET'])