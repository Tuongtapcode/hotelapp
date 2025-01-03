from email.quoprimime import quote

from sqlalchemy import func, desc, extract, and_, or_
from app.models import Room, RoomType, RoomStatus, User, Account, Customer, AccountRole, BookingRoom, BookingStatus, \
    Bill
from app import app, db
import hashlib
from datetime import datetime, date, timedelta
import calendar
from calendar import monthrange


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
#Hàm đếm tổng phòng.
def count_room():
    return Room.query.count()

#hàm đềm phòng có status là Available
def count_available_rooms():
    available_status_id = db.session.query(RoomStatus.id).filter(RoomStatus.name == "Available").scalar()
    if available_status_id:
        count = db.session.query(func.count(Room.id)).filter(Room.room_status_id == available_status_id).scalar()
        return count
    return 0


# Số khách hiện có trong phòng
def count_guests_per_room():
    return db.session.query(
        Room.id.label("room_id"),
        Room.name.label("room_name"),
        func.count(BookingRoom.customer_id).label('So_khach')
    ).join(BookingRoom, Room.id == BookingRoom.room_id) \
        .filter(
        BookingRoom.booking_status_id == 2,
        (BookingRoom.checkin <= datetime.now()) &  # Check-in đã xảy ra
        ((BookingRoom.checkout >= datetime.now()) | (BookingRoom.checkout == None))
        # Check-out là NULL hoặc trong tương lai
    ) \
        .group_by(
        Room.id
    ) \
        .all()



### Tổng doanh thu theo tháng
# def revenue_by_month(year=datetime.now().year, month=datetime.now().month ):
#     return db.session.query(
#         func.extract('month', Bill.issue_date).label('month'),  # Lấy tháng từ ngày tạo hóa đơn
#         func.sum(Bill.total_amount).label('total_revenue')  # Tổng doanh thu trong tháng
#     ).filter(
#         func.extract('year', Bill.issue_date) == year  # Lọc theo năm cụ thể
#     ).group_by(
#         func.extract('month', Bill.issue_date)  # Nhóm theo tháng
#     ).order_by(
#         func.extract('month', Bill.issue_date)  # Sắp xếp theo tháng
#     ).all()


# Đếm doanh thu từng ngày trong tháng
def revenue_by_day(year=datetime.now().year, month=datetime.now().month):
    days_in_month = calendar.monthrange(year, month)[1]  # Số ngày trong tháng
    all_days = [date(year, month, day) for day in range(1, days_in_month + 1)]

    # Truy vấn doanh thu từ cơ sở dữ liệu
    revenue_data = db.session.query(
        func.extract('day', Bill.issue_date).label('issue_date'),  # Ngày
        func.sum(Bill.total_amount).label('total_revenue')  # Tổng doanh thu
    ).filter(
        func.extract('year', Bill.issue_date) == year,
        func.extract('month', Bill.issue_date) == month
    ).group_by(
        func.extract('day', Bill.issue_date)
    ).all()

    # Chuyển kết quả thành dictionary để dễ xử lý
    revenue_dict = {int(issue_date): revenue for issue_date, revenue in revenue_data}
    # Kết hợp tất cả các ngày với dữ liệu doanh thu
    result = []
    for day in all_days:
        if day.day in revenue_dict:
            revenue = revenue_dict[day.day]
        else:
            revenue = 0
        result.append((day.day, revenue))
    return result





# Doanh thu, lượt thuê phòng theo RoomType
def revenue_roomtype_report_by_month(year=datetime.now().year, month=datetime.now().month):
    # Subquery để tính doanh thu và lượt thuê theo RoomType
    subquery = db.session.query(
        Room.room_type_id.label("room_type_id"),
        func.sum(Bill.total_amount).label("revenue"),
        func.count(Bill.id).label("booking_count")
    ).join(BookingRoom, Room.id == BookingRoom.room_id) \
        .join(Bill, BookingRoom.id == Bill.booking_room_id) \
        .filter(
        func.extract('year', Bill.issue_date) == year,
        func.extract('month', Bill.issue_date) == month
    ) \
        .group_by(Room.room_type_id) \
        .subquery()

    # Outer join với RoomType để đảm bảo tất cả các loại phòng xuất hiện
    results = db.session.query(
        RoomType.name.label("room_type"),
        func.coalesce(subquery.c.revenue, 0).label("revenue"),  # Doanh thu mặc định là 0 nếu không có dữ liệu
        func.coalesce(subquery.c.booking_count, 0).label("booking_count"),# Lượt thuê mặc định là 0 nếu không có dữ liệu
        (subquery.c.booking_count / func.sum(subquery.c.booking_count).over().label('Percentage')) * 100
    ).join(subquery, RoomType.id == subquery.c.room_type_id) \
        .order_by(desc("revenue"))\
        .all()
    return results

#Hàm trả về số ngày thuê của mỗi phòng / tháng
def get_days_rented_in_month(year=datetime.now().year, month=datetime.now().month, status_id=3):
    # Xác định ngày đầu và cuối của tháng
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, monthrange(year, month)[1])
    total_days_in_month = (end_date - start_date).days + 1
    results = (
        db.session.query(
            Room.name.label('Tên phòng'),
            func.coalesce(
                func.sum(
                    func.datediff( # tính số ngày giữa hai ngày.
                        func.least(BookingRoom.checkout, end_date), #Lấy ngày sớm nhất giữa 2 ngày
                        func.greatest(BookingRoom.checkin, start_date) #Lấy ngày muộn nhất giữa 2 ngày
                    ) + 1
                ),
               0
            ).label('Số ngày thuê'),
            func.coalesce(
                (func.sum(
                    func.datediff(
                        func.least(BookingRoom.checkout, end_date),
                        func.greatest(BookingRoom.checkin, start_date)
                    ) + 1
                ) / total_days_in_month * 100),
                0
            ).label('Tỷ lệ')
        )
        .outerjoin(BookingRoom, Room.id == BookingRoom.room_id)  # Dùng kêt trái để hiển thị tất cả các phòng
        .filter(
            (BookingRoom.checkin <= end_date) | (BookingRoom.checkin == None),
            # Checkin trước hoặc bằng ngày cuối tháng hoặc không có booking
            (BookingRoom.checkout >= start_date) | (BookingRoom.checkout == None),
            # Checkout sau hoặc bằng ngày đầu tháng hoặc không có booking
            (BookingRoom.booking_status_id == status_id) | (BookingRoom.booking_status_id == None)
            # Hoặc trạng thái không tồn tại
        )
        .group_by(Room.id)
        .all()
    )
    return results


#Bảng mật độ sử dụng phòng
def get_room_statistics(year=datetime.now().year, month=datetime.now().month):
    # Truy vấn và lọc theo trạng thái booking, tháng và năm
    subquery = db.session.query(
        Room.id,
        Room.name,
        func.coalesce(func.count(BookingRoom.start_day.distinct()), 0).label('rented_days')  # Thay NULL bằng 0
    ).outerjoin(  # Dùng outerjoin để lấy tất cả các phòng
        BookingRoom, BookingRoom.room_id == Room.id  # Liên kết giữa BookingRoom và Room
    ).filter(
        (BookingRoom.booking_status_id == 3) | (BookingRoom.booking_status_id == None),
        # Lọc theo trạng thái booking là 3 hoặc không có booking
        (extract('month', BookingRoom.start_day) == month) | (BookingRoom.start_day == None),
        # Lọc theo tháng hoặc không có booking
        (extract('year', BookingRoom.start_day) == year) | (BookingRoom.start_day == None)
        # Lọc theo năm hoặc không có booking
    ).group_by(
        Room.id
    ).subquery()
    return db.session.query(
        subquery.c.name,  # Tên phòng
        subquery.c.rented_days,  # Số ngày thuê của mỗi phòng
        (subquery.c.rented_days / func.sum(subquery.c.rented_days).over().label('Percentage')) * 100
    ).all()

#tính số công suất khách trong phong từng ngày trong tháng
def get_room_capacity(year=datetime.now().year, month=datetime.now().month):
    # Tính ngày đầu tiên và ngày cuối cùng của tháng
    start_date = datetime(year, month, 1).date()  # Chuyển thành datetime.date
    end_date =datetime.now().date()  # Chuyển thành datetime.date

    # Tạo một subquery để lấy danh sách các booking với trạng thái check-in hoặc check-out
    bookings = db.session.query(
        BookingRoom.id,
        BookingRoom.checkin,
        BookingRoom.checkout,
        BookingRoom.room_id,
        BookingRoom.booking_status_id
    ).filter(
        or_(
            BookingRoom.booking_status_id == 2,  # check-in
            BookingRoom.booking_status_id == 3  # check-out
        )
    ).all()

    # Khởi tạo một dictionary để lưu số lượng phòng đã được sử dụng trong từng ngày
    room_usage = {(start_date + timedelta(days=i)).day: 0 for i in range((end_date - start_date).days + 1)}

    # Duyệt qua từng booking và tính số phòng được sử dụng
    for booking in bookings:
        checkin_date = booking.checkin.date()  # Lấy phần ngày của checkin
        checkout_date = booking.checkout.date()  # Lấy phần ngày của checkout

        # Duyệt qua tất cả các ngày trong khoảng từ checkin đến checkout
        current_date = checkin_date
        while current_date <= checkout_date:
            if start_date <= current_date <= end_date:
                room_usage[current_date.day] += 1
            current_date += timedelta(days=1)

    # Trả về danh sách với định dạng [(ngày trong tháng, số lượng phòng)]
    return [(day, count) for day, count in room_usage.items()]


def bill_recent_activities():
    # Lấy 5 hóa đơn gần nhất
    return db.session.query(Bill).order_by(desc(Bill.issue_date)).limit(5).all()


if __name__ == "__main__":
    with app.app_context():
        print(get_room_capacity())
