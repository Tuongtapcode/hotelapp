from sqlalchemy.orm import query_expression

from app.models import Room, RoomPrice, RoomType, RoomStatus, User, Account, Customer, AccountRole, BookingRoom
from app import app, db
import hashlib
from datetime import datetime


def load_rooms():
    query = Room.query
    return query.all()


def load_status_room():
    query = RoomStatus.query.all()
    return query


def load_room_types():
    query = RoomType.query.all()
    return query


def load_layer():
    rooms = Room.query.all()
    layers = sorted(set(str(room.id)[0] for room in rooms))
    return layers


def search_rooms_direct(room_type_id=None, max_occupancy=None, room_price=None, room_status_id=None, layer=None):
    query = Room.query
    if room_type_id:
        query = query.filter(Room.room_type_id == int(room_type_id))
    if max_occupancy:
        query = query.filter(Room.max_occupancy >= max_occupancy)
    if room_price:
        rooms = query.all()
        rooms = [room for room in rooms if room.room_price.price_per_night <= room_price]
        return rooms
    if room_status_id:
        query = query.filter(Room.room_status_id == int(room_status_id))
    if layer:
        query = query.filter(Room.id.like(f"{layer}%"))
    return query.all()


def auth_account(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    a = Account.query.filter(Account.username.__eq__(username),
                             Account.password.__eq__(password))

    if role:
        a = a.filter(Account.role.__eq__(role))
    return a.first()


def add_user_account(full_name, email, username, password):
    try:
        # Băm mật khẩu
        hashed_password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        # Tạo đối tượng Customer (kế thừa User)
        new_customer = Customer(
            name=full_name,
            email=email,
            type='customer'  # Phân loại là 'customer'
        )

        # Tạo đối tượng Account
        new_account = Account(
            username=username,
            password=hashed_password,
            user=new_customer,  # Liên kết với Customer
            role='USER'  # Mặc định là USER
        )

        # Thêm vào phiên
        db.session.add(new_customer)
        db.session.add(new_account)

        # Commit thay đổi
        db.session.commit()
        return True

    except Exception as e:
        app.logger.error(f"Error adding user: {e}")
        db.session.rollback()
        return False


def create_booking(room, staff, customer, checkin, checkout):
    staff_id = staff.id if staff else None
    booking = BookingRoom(
        start_day=datetime.now(),
        checkin=checkin,
        checkout=checkout,
        room_id=room.id,
        staff_id=staff_id,
        customer_id=customer.id
    )
    db.session.add(booking)
    db.session.commit()
    return booking



############
def get_room_by_id(room_id):
    return Room.query.get(room_id)

def update_room_status(room_id, new_status):
    room = get_room_by_id(room_id)
    status = RoomStatus.query.filter_by(name=new_status).first()
    if room and status:
        room.room_status_id = status.id
        db.session.commit()


def book_room(room_id, start_day, customer_id):
    room = get_room_by_id(room_id)
    if room and room.room_status.name == 'Available':
        booking = BookingRoom(
            start_day=start_day,
            checkin=datetime.now(),
            checkout=None,
            room_id=room_id,
            customer_id=customer_id
        )
        update_room_status(room_id, 'Booked')
        db.session.add(booking)
        db.session.commit()
