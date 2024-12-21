from click import launch
from flask import Blueprint, render_template, request
import dao
from app.models import room_statuses
from datetime import datetime, date

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
    cus = dao.load_cus()
    current_time = datetime.now()
    bookings = dao.loaf_booking_room()

    rooms = dao.search_rooms_direct(room_type_id, max_occupancy, room_price, room_status_id, layer)
    return render_template('staff/rooms.html', rooms=rooms, room_statuses=room_statuses, layers=layers,
                           room_types=room_types, cus=cus, current_time=current_time, bookings=bookings)


@staff_bp.route('/rooms/cancel_booking', methods=['POST'])
def cancel_booking():
    room_id = request.form.get('room_id')
    room = dao.get_room_by_id(room_id)

    if room and room.room_status.name == "Booked":
        dao.update_room_status(room_id, "Available")  # Cập nhật trạng thái phòng thành "Available"
        return jsonify({'success': True, 'message': 'Đặt phòng đã được hủy.'})
    else:
        return jsonify(
            {'success': False, 'message': 'Không/rooms/checkin thể hủy đặt phòng. Vui lòng kiểm tra trạng thái phòng.'})


@staff_bp.route('/rooms/checkin', methods=['POST'])
def checkin_room():
    data = request.json  # Đọc dữ liệu JSON
    room_id = data.get('room_id')  # Lấy room_id từ JSON
    room = dao.get_room_by_id(room_id)

    if room and room.room_status.name == "Booked":
        dao.update_room_status(room_id, "Checked")
        return jsonify({'success': True, 'message': 'Phòng đã được nhận (Check-in).'})
    else:
        return jsonify({'success': False, 'message': 'Không thể nhận phòng. Vui lòng kiểm tra trạng thái phòng.'})


@staff_bp.route('/customers')
def customers_view():
    return render_template('staff/customers.html')


@staff_bp.route('/rooms/book', methods=['POST'])
def book_room():
    customerName = request.form.get('customerName')
    customer_identification_number = request.form.get('customer_identification_number')
    room_id = request.form.get('room_id')  # ID của phòng cần thuê
    checkin_date = request.form.get('checkin_date')

    return redirect('staff/dashboard')
