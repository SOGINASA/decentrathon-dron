from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_models import Admin, db, User, Order

user_bp = Blueprint('user', __name__)

def create_order():
    if current_user.is_authenticated:
        if request.method == 'POST':
            start_location = request.form.get('start_location')
            end_location = request.form.get('end_location')
            cost = request.form.get('cost')
            order = Order(start_location=start_location, end_location=end_location, owner_id=current_user.id, status='in_queue', cost=cost)
            db.session.add(order)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('order.html')
    return redirect('/auth/login')

def my_queue():
    if current_user.is_authenticated:
        orders_unfiltred = Order.query.filter_by(owner_id=current_user.id).all()
        orders = []
        for i in orders_unfiltred:
            if i.status == 'in_queue' or i.status == 'in_progress':
                orders.append(i)
        return render_template('queue.html', orders=orders)
    return redirect('/auth/login')

def dashboard():
    if current_user.is_authenticated:
        orders_unfiltred = Order.query.filter_by(owner_id=current_user.id).all()
        orders = []
        for i in orders_unfiltred:
            if i.status == 'in_queue' or i.status == 'in_progress':
                orders.append(i)
        return render_template('us_main.html', orders=orders[:5])
    return redirect('/auth/login')

def profile():
    if current_user.is_authenticated:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            user_exist = User.query.filter_by(username=name).first()
            admin_exist = Admin.query.filter_by(username=name).first()

            if user_exist or admin_exist:
                return render_template('profile.html', error="Пользователь с таким именем уже существует")

            user = User.query.filter_by(id=current_user.id).first()
            user.username = name
            user.email = email
            if password:
                user.set_password(password)
            db.session.commit()
            return redirect('/')

        return render_template('profile.html')
    return redirect('/auth/login')

user_bp.add_url_rule('/create_order', view_func=create_order, methods=['GET', 'POST'])
user_bp.add_url_rule('/queue', view_func=my_queue, methods=['GET'])
user_bp.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])
user_bp.add_url_rule('/profile', view_func=profile, methods=['GET', 'POST'])
