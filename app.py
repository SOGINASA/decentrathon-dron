from flask import Flask, render_template, redirect, session
import os
from flask_login import LoginManager, current_user

from db_models import db, User, Admin, Drone, Order
from routes import auth_bp, admin_bp, user_bp

# Инициализация приложения
app = Flask(
    __name__,
    template_folder='view/templates',
    static_folder='view/static'
)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    if not user_id or user_id == "None":
        return None
    return User.query.get(int(user_id))

# Главная страница (Мониторинг)
@app.route('/', endpoint='index')
def index():
    if not current_user.is_authenticated:
        return redirect('/auth/register')
    if current_user.is_admin:
        return redirect('/admin/dashboard')
    else:
        return redirect('/user/dashboard')

# Страница миссий
@app.route('/missions', endpoint='missions')
def missions():
    if not current_user.is_authenticated:
        return redirect('/auth/login')
    return render_template('missions.html')

# Страница логов
@app.route('/logs', endpoint='logs')
def logs():
    if not current_user.is_authenticated:
        return redirect('/auth/login')
    return render_template('logs.html')

# Страница дронов
@app.route('/drones', endpoint='drones')
def drones():
    if not current_user.is_authenticated:
        return redirect('/auth/login')
    return render_template('drones.html')

# Страница пилотов
@app.route('/pilots', endpoint='pilots')
def pilots():
    if not current_user.is_authenticated:
        return redirect('/auth/login')
    return render_template('pilots.html')

# Роуты аутентификации (login, register, logout)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
