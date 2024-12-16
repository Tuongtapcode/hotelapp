from click import launch
from flask import Blueprint, render_template, request
import dao
from app.models import room_statuses

staff_bp = Blueprint('staff', __name__, template_folder='templates/staff')


@staff_bp.route('/dashboard')
def dashboard_view():
    return render_template('staff/dashboard.html')


@staff_bp.route('/rooms')
def rooms_view():
    layers = dao.load_layer()
    room_statuses = dao.load_status_room()
    room_types = dao.load_room_types()

    room_type_id = request.args.get('room_type_id')
    max_occupancy = None
    room_price = None
    room_status_id = request.args.get('room_status_id')
    layer = request.args.get('layer', default=None)

    rooms = dao.search_rooms_direct(room_type_id, max_occupancy, room_price, room_status_id, layer)

    return render_template('staff/rooms.html', rooms=rooms, room_statuses=room_statuses, layers=layers,
                           room_types=room_types)


@staff_bp.route('/customers')
def customers_view():
    return render_template('staff/customers.html')


@staff_bp.route('/room/<int:room_id>', methods=['GET'])
def get_room_status(room_id):
    room = Room.query.get(room_id)
    if room:
        return jsonify({
            "id": room.id,
            "status": room.room_status.name,
            "name": room.name,
            "price": room.room_price.price_per_night
        })
    return jsonify({"error": "Room not found"}), 404


@staff_bp.route('/rooms/book', methods=['POST'])
def book_room():
    data = request.json
    room = Room.query.get(data['room_id'])
    if room and room.room_status.name == 'Available':
        room.room_status_id = 2  # Assuming 2 is the ID for 'Checked'
        db.session.commit()
        return jsonify({"message": "Room booked successfully"})
    return jsonify({"error": "Room is not available"}), 400


@staff_bp.route('/rooms/checkout', methods=['POST'])
def checkout_room():
    data = request.json
    room = Room.query.get(data['room_id'])
    if room and room.room_status.name == 'Checked':
        room.room_status_id = 1  # Assuming 1 is the ID for 'Available'
        db.session.commit()
        return jsonify({"message": "Room checked out successfully"})
    return jsonify({"error": "Room is not checked in"}), 400


