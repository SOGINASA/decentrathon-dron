from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_models import Admin, db, User



auth_bp = Blueprint('auth', __name__)


def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        print(user.username)
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            session['username'] = username
            session['is_admin'] = True
            return redirect('/')
        
        if user and user.check_password(password):
            login_user(user)
            session['username'] = username
            session['is_admin'] = 'user'
            return redirect('/')
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль")
    
    return render_template('login.html')

# Страница регистрации
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Проверка, существует ли пользователь
        existing_user = User.query.filter_by(username=username).first()
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_user or existing_admin:
            return render_template('register.html')
        
        # Создание нового пользователя
        new_user = User(username=username, email=email)
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
    
    return render_template('register.html')

def register_admin():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Проверка, существует ли пользователь
        existing_user = User.query.filter_by(username=username).first()
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_user or existing_admin:
            return render_template('register.html')
        
        # Создание нового пользователя
        new_admin = Admin(username=username, email=email)
        new_admin.set_password(password)
        
        try:
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при регистрации: {str(e)}", 500

        
        login_user(new_admin)
        session['username'] = username
        session['is_admin'] = True
        return redirect('/')
    
    return render_template('register.html')


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