from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_models import Admin, db, User

user_bp = Blueprint('user', __name__)

def create_order():
    if current_user.is_authenticated:
        if method == 'POST':
            start_location = request.form.get('start_location')
            end_location = request.form.get('end_location')
            cost = request.form.get('cost')
            order = Order(start_location=start_location, end_location=end_location, owner_id=current_user.id, status='in_queue', cost=cost)
            db.session.add(order)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('create_order.html')
    return redirect('/auth/login')

def my_queue():
    if current_user.is_authenticated:
        orders_unfiltred = Order.query.filter_by(owner_id=current_user.id).all()
        orders = []
        for i in orders_unfiltred:
            if i.status == 'in_queue' or i.status == 'in_progress':
                orders.append(i)
        return render_template('my_queue.html', orders=orders)
    return redirect('/auth/login')

def dashboard():
    if current_user.is_authenticated:
        orders_unfiltred = Order.query.filter_by(owner_id=current_user.id).all()
        orders = []
        for i in orders_unfiltred:
            if i.status == 'in_queue' or i.status == 'in_progress':
                orders.append(i)
        return render_template('my_queue.html', orders=orders[:5])
    return redirect('/auth/login')

user_bp.route('/create_order', methods=['GET', 'POST'])
user_bp.route('/queue', methods=['GET'])
user_bp.route('/dashboard', methods=['GET'])
