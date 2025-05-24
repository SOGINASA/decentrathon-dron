from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_models import Admin, db, User, Order

user_bp = Blueprint('user', __name__)

def create_order():
    if current_user.is_authenticated:
        if request.method == 'POST':
            # Получаем адреса — можно сохранить как есть, если нужно, либо убрать
            start_location = request.form.get('start_location')  # Можно сохранить, если надо
            end_location = request.form.get('end_location')      # Можно сохранить, если надо

            # Получаем координаты из скрытых полей
            start_lat = request.form.get('start_lat', type=float)
            start_lon = request.form.get('start_lon', type=float)
            end_lat = request.form.get('end_lat', type=float)
            end_lon = request.form.get('end_lon', type=float)
            time = request.form.get('time')

            cost = request.form.get('cost', type=int)

            # Создаём объект заказа с координатами
            order = Order(
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
                owner_id=current_user.id,
                status='in_queue',
                cost=cost,
                time=time,
                start_location=start_location,
                end_location=end_location
            )
            db.session.add(order)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('order.html', city_lat=current_user.city_lat, city_lng=current_user.city_lng)
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

def support():
    return render_template('support.html')

def get_all_orders():
    orders = Order.query.all()
    orders_list = []
    for order in orders:
        orders_list.append({
            'id': order.id,
            'start_lat': order.start_lat,
            'start_lon': order.start_lon,
            'end_lat': order.end_lat,
            'end_lon': order.end_lon,
            'owner_id': order.owner_id,
            'status': order.status,
            'cost': order.cost,
            'time': order.time,
            'start_location': order.start_location,
            'end_location': order.end_location
        })
    return jsonify(orders_list)


from flask import request
from functools import wraps



API_TOKEN = "your-secret-api-token"

def require_api_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return decorated

@require_api_token
def start_order(order_id):

    if not order_id:
        return jsonify({'error': 'Missing order_id or owner_id'}), 400

    try:
        order = Order.query.filter_by(id=order_id).first_or_404()
        order.status = 'in_progress'
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Order started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


user_bp.add_url_rule('/create_order', view_func=create_order, methods=['GET', 'POST'])
user_bp.add_url_rule('/queue', view_func=my_queue, methods=['GET'])
user_bp.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])
user_bp.add_url_rule('/profile', view_func=profile, methods=['GET', 'POST'])
user_bp.add_url_rule('/support', view_func=support, methods=['GET'])
user_bp.add_url_rule('/orders', view_func=get_all_orders, methods=['GET'])
user_bp.add_url_rule('/orders/<int:order_id>/start', view_func=start_order, methods=['POST'])