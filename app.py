from flask import Flask, redirect, session
import os
from flask_login import LoginManager, current_user
from flask_cors import CORS

from db_models import Admin, db, User
from routes import auth_bp, admin_bp, user_bp, api_bp

# Инициализация приложения
app = Flask(
    __name__,
    template_folder='view/templates',
    static_folder='view/static'
)
CORS(app)
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
    if not user_id:
        return None
    try:
        user_type, username = user_id.split(":", 1)
        if user_type == "user":
            return User.query.filter_by(username=username).first()
        elif user_type == "admin":
            return Admin.query.filter_by(username=username).first()
    except ValueError:
        return None


# Главная страница (Мониторинг)
@app.route('/', endpoint='index')
def index():
    if not current_user.is_authenticated:
        return redirect('/auth/register')
    if session.get('is_admin'):
        return redirect('/admin/dashboard')
    else:
        return redirect('/user/dashboard')


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)