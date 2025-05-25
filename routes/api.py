from flask import jsonify, request, Blueprint
from db_models import db, Log, Order


api_bp = Blueprint('api', __name__)


def get_active_orders():
    orders = Order.query.filter(Order.status == 'in_queue').all()
    result = []
    for o in orders:
        result.append({
            'id': o.id,
            'start': [o.start_lat, o.start_lon],
            'end': [o.end_lat, o.end_lon],
            'start_time': o.date.isoformat(),
            'speed': 1
        })
    return jsonify(result)

def queue_api():
    orders = Order.query.filter(Order.status == 'in_queue').all()
    return jsonify(orders)

def set_active_orders(order_id):
    order = Order.query.filter(Order.id == order_id).first()
    order.status = 'in_progress'
    db.session.commit()

def complete_order(order_id):
    order = Order.query.filter(Order.id == order_id).first()
    order.status = 'completed'
    db.session.commit()

def add_log():
    message = request.args.get('message')
    log = Log(message=message)
    db.session.add(log)
    db.session.commit()

api_bp.add_url_rule('/active_orders', view_func=get_active_orders, methods=['GET'])
api_bp.add_url_rule('/queue', view_func=queue_api, methods=['GET'])
api_bp.add_url_rule('/set_active_orders/<int:order_id>', view_func=set_active_orders, methods=['POST'])
api_bp.add_url_rule('/complete_order/<int:order_id>', view_func=complete_order, methods=['POST'])
api_bp.add_url_rule('/add_log', view_func=add_log, methods=['POST'])