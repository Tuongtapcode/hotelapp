from email.quoprimime import quote

from sqlalchemy import func

from app.models import Room, RoomType, RoomStatus, User, Account, Customer, AccountRole, BookingRoom, BookingStatus, Bill
from app import app, db
import hashlib
from datetime import datetime


def loaf_booking_room():
    query = BookingRoom.query
    return query.all()


def load_rooms():
    query = Room.query
    return query.all()


def load_cus():
    query = Customer.query
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


def search_rooms_direct(room_type_id=None, max_occupancy=None, room_status_id=None, layer=None):
    # Khởi tạo query cơ bản
    query = Room.query

    # Thêm các bộ lọc tùy chọn
    if room_type_id:
        query = query.filter(Room.room_type_id == int(room_type_id))
    if max_occupancy:
        query = query.filter(Room.max_occupancy >= max_occupancy)
    if room_status_id:
        query = query.filter(Room.room_status_id == int(room_status_id))
    if layer:
        query = query.filter(Room.id.like(f"{layer}%"))

    # Nếu room_price được cung cấp, lọc thủ công các phòng theo giá

    # Kết thúc bằng truy vấn và trả về kết quả
    return query.options(db.joinedload(Room.rooms_booking)).all()


def auth_account(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    a = Account.query.filter(Account.username.__eq__(username),
                             Account.password.__eq__(password))

    if role:
        a = a.filter(Account.role.__eq__(role))
    return a.first()


def add_user_account(full_name, email, username, password, identification_number, nationality):
    try:
        # Băm mật khẩu
        hashed_password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        # Tạo đối tượng Customer (kế thừa User)
        new_customer = Customer(
            name=full_name,
            email=email,
            identification_number=identification_number,
            nationality=nationality,
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
    if room and room.room_status.name == 'Available':
        booking = BookingRoom(
            start_day=datetime.now(),
            checkin=checkin,
            checkout=checkout,
            room_id=room.id,
            staff_id=staff_id,
            customer_id=customer.id
        )
    return booking


############
def get_room_by_id(room_id):
    return Room.query.get(room_id)


def get_booking_for_room(room_id):
    booking = db.session.query(BookingRoom).filter(BookingRoom.room_id == room_id).first()
    if booking:
        return booking
    else:
        return None


def update_room_status(room_id, new_status):
    room = get_room_by_id(room_id)
    status = RoomStatus.query.filter_by(name=new_status).first()
    if room and status:
        room.room_status_id = status.id
        db.session.commit()


def book_room(room, staff, customer, checkin, checkout):
    booking = create_booking(room, staff, customer, checkin, checkout)
    update_room_status(room.id, 'Booked')
    db.session.add(booking)
    db.session.commit()
    return booking


def rent_room():
    customer = Customer.query.filter_by(identification_number=customer_id_number).first()
    if not customer:
        customer = Customer(
            name=customer_name,
            identification_number=customer_id_number
        )
        db.session.add(customer)
    update_room_status(room.id, 'Ckecked')


###### Thống kê báo cao
def count_room():
    return Room.query.count()


def count_available_rooms():
    available_status_id = db.session.query(RoomStatus.id).filter(RoomStatus.name == "Available").scalar()
    if available_status_id:
        count = db.session.query(func.count(Room.id)).filter(Room.room_status_id == available_status_id).scalar()
        return count
    return 0


def count_guests_per_room():
    return db.session.query(
        Room.name.label("room_name"),
        func.coalesce(func.count(BookingRoom.customer_id), 0).label("guest_count"),
        BookingRoom.booking_status_id.label("booking_status_id"),
        BookingStatus.name.label("booking_status")
    ).outerjoin(BookingRoom, Room.id == BookingRoom.room_id) \
        .outerjoin(BookingStatus, BookingRoom.booking_status_id == BookingStatus.id) \
        .filter(
        (BookingRoom.checkin <= datetime.now()) &
        ((BookingRoom.checkout >= datetime.now()) | (BookingRoom.checkout == None))

    ) \
        .group_by(Room.id, BookingRoom.booking_status_id, BookingStatus.name) \
        .all()

def revenue_by_month(year=datetime.now().year):
    return db.session.query(
        func.extract('month', Bill.issue_date).label('month'),  # Lấy tháng từ ngày tạo hóa đơn
        func.sum(Bill.total_amount).label('total_revenue')  # Tổng doanh thu trong tháng
    ).filter(
        func.extract('year', Bill.issue_date) == year  # Lọc theo năm cụ thể
    ).group_by(
        func.extract('month', Bill.issue_date)  # Nhóm theo tháng
    ).order_by(
        func.extract('month', Bill.issue_date)  # Sắp xếp theo tháng
    ).all()


if __name__ == "__main__":
    with app.app_context():
        print(count_guests_per_room())
