from flask import redirect, render_template, request, session, url_for, Blueprint
from flask_login import login_required, login_user, logout_user
from db_models import Admin, db, User



auth_bp = Blueprint('auth', __name__)


def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            session['username'] = username
            session['is_admin'] = True
            return redirect('/')
        
        if user and user.check_password(password):
            login_user(user)
            session['username'] = username
            session['is_admin'] = False
            return redirect('/')
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль")
    
    return render_template('login.html')

# Страница регистрации
def register():
    popular_cities_kz = [
        {"name": "Алматы", "lat": 43.238949, "lon": 76.889709},
        {"name": "Астана", "lat": 51.160523, "lon": 71.470356},
        {"name": "Шымкент", "lat": 42.341736, "lon": 69.590099},
        {"name": "Караганда", "lat": 49.8047, "lon": 73.1094},
        {"name": "Актобе", "lat": 50.2839, "lon": 57.166},
        {"name": "Тараз", "lat": 42.9, "lon": 71.3667},
        {"name": "Павлодар", "lat": 52.2871, "lon": 76.9674},
        {"name": "Усть-Каменогорск", "lat": 49.9574, "lon": 82.6142},
        {"name": "Кызылорда", "lat": 44.8488, "lon": 65.4823},
        {"name": "Семей", "lat": 50.411, "lon": 80.2275},
        {"name": "Петропавловск", "lat": 54.8706, "lon": 69.1913}
    ]

    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        selected_city = request.form.get('city')

        existing_user = User.query.filter_by(username=username).first()
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_user or existing_admin:
            return render_template('register.html', cities=popular_cities_kz, error="Пользователь уже существует")

        # Получение координат города
        city_data = next((city for city in popular_cities_kz if city["name"] == selected_city), None)
        if not city_data:
            return render_template('register.html', cities=popular_cities_kz, error="Выберите корректный город")

        new_user = User(
            username=username,
            email=email,
            city_lat=city_data["lat"],
            city_lng=city_data["lon"]
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при регистрации: {str(e)}", 500

        login_user(new_user)
        session['username'] = username
        session['is_admin'] = False
        return redirect('/')

    return render_template('register.html', cities=popular_cities_kz)

def register_admin():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Проверка, существует ли пользователь
        existing_user = User.query.filter_by(username=username).first()
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_user or existing_admin:
            return render_template('register_admin.html')
        
        # Создание нового пользователя
        new_admin = Admin(username=username, email=email)
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()

        
        login_user(new_admin)
        session['username'] = username
        session['is_admin'] = True
        return redirect('/')
    
    return render_template('register_admin.html')


# Выход

@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))


auth_bp.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
auth_bp.add_url_rule('/register_admin', view_func=register_admin, methods=['GET', 'POST'])
auth_bp.add_url_rule('/login', view_func=login, methods=['GET','POST'])
auth_bp.add_url_rule('/logout', view_func=logout, methods=['GET'])

if __name__ == '__main__':
    print('wrong file')