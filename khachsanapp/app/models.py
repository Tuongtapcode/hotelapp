from email.mime import image
import hashlib
from sqlalchemy import Table,Column, Integer, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship, backref
from app import app, db
from enum import Enum as RoleEnum
from flask_login import UserMixin, LoginManager
from datetime import datetime


class AccountRole(RoleEnum):
    ADMIN = 1
    STAFF = 2
    USER = 3


class Hotel(db.Model):
    # __tablename__ = 'hotel'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # Hotel name
    address = Column(String(200), nullable=False)
    rooms = relationship('Room', backref='hotel', cascade="all, delete-orphan")

    def __str__(self):
        return self.name


class User(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)  # 'type' for polymorphic inheritance
    name = Column(String(50), nullable=False)
    phone = Column(String(10))
    email = Column(String(50))
    address = Column(String(200))
    account = relationship("Account", back_populates="user", uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': 'user',  # Set polymorphic identity
        'polymorphic_on': type  # Set which column will store the polymorphic type
    }


class Account(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Mật khẩu nên mã hóa
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)  # Khóa ngoại
    user = relationship("User", back_populates="account")  # Quan hệ 1-1 với User
    role = Column(Enum(AccountRole), default=AccountRole.USER)  # Thêm vai trò vào tài khoản


class Customer(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    rooms_booking = relationship('BookingRoom', backref='customer', lazy=True)
    identification_number = Column(String(20), nullable=False)
    nationality = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'customer',  # Set polymorphic identity for Customer
    }


class Staff(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    rooms_booking = relationship('BookingRoom', backref='staff', lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'staff',  # Set polymorphic identity for Customer
    }


class RoomStatus(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    rooms = relationship("Room", backref="room_status", lazy=True)
    description = Column(String(255), nullable=True)

    def __str__(self):
        return self.name


class RoomType(db.Model):
    # __tablename__ = 'RoomType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    price_per_night = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    rooms = relationship("Room", backref="room_type", lazy=True)

    def __str__(self):
        return self.name


class BookingStatus(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    rooms_booking = relationship("BookingRoom", backref="booking_status", lazy=True)


class Room(db.Model):
    id = Column(String(10), primary_key=True)
    name = Column(String(50), unique=True)
    max_occupancy = Column(Integer)
    room_type_id = Column(Integer, ForeignKey('room_type.id'), nullable=False)
    room_status_id = Column(Integer, ForeignKey('room_status.id'), nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)
    rooms_booking = relationship('BookingRoom', backref='BookingRoom', lazy=True)
    image = Column(String(200), nullable=False)
    size = Column(Float)

    def __str__(self):
        return self.name or "Unnamed Room"


booking_room_coefficient = Table(
    'booking_room_coefficient',
    db.metadata,
    Column('coefficient_id', Integer, ForeignKey('coefficient.id'), primary_key=True),
    Column('booking_room_id', Integer, ForeignKey('booking_room.id'), primary_key=True)
)


class Coefficient(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # Tên hệ số
    description = Column(String(255), nullable=True)  # Mô tả
    booking_rooms = relationship(
        'BookingRoom',
        secondary=booking_room_coefficient,
        back_populates='coefficients'
    )

    def __repr__(self):
        return f"<Coefficient(id={self.id}, name='{self.name}')>"


class BookingRoom(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_day = Column(DateTime, nullable=False, default=datetime.now())
    checkin = Column(DateTime, nullable=False, default=datetime.now())
    checkout = Column(DateTime, nullable=False, default=datetime.now())
    room_id = Column(String(10), ForeignKey('room.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    bill = relationship("Bill", back_populates="booking_room", uselist=False)
    booking_status_id = Column(Integer, ForeignKey('booking_status.id'), nullable=False, default=1)
    coefficients = relationship(
        'Coefficient',
        secondary='booking_room_coefficient',
        back_populates='booking_rooms'
    )


class Bill(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_amount = Column(Float, nullable=False)  # Tổng số tiền hóa đơn
    issue_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Ngày tạo hóa đơn
    booking_room_id = Column(Integer, ForeignKey('booking_room.id'), nullable=False, unique=True)  # 1-1 với BookingRoom
    booking_room = relationship("BookingRoom", back_populates="bill", uselist=False)  # 1-1 với BookingRoom
    payments = relationship('Payment', backref='bill', cascade="all, delete-orphan")  # 1-nhiều với Payment

    def __repr__(self):
        return f"<Bill(id={self.id}, total_amount={self.total_amount}, issue_date={self.issue_date})>"


class Payment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)  # Số tiền thanh toán
    method = Column(String(50), nullable=False)  # Phương thức thanh toán
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Ngày thanh toán
    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=False)  # Khóa ngoại liên kết đến Bill

    def __repr__(self):
        return f"<Payment(method='{self.method}', amount={self.amount}, date={self.payment_date})>"


class DomesticCustomer(Customer):
    id = Column(Integer, ForeignKey('customer.id'), primary_key=True)
    national_id = Column(String(12), nullable=False)  # CMND/CCCD

    __mapper_args__ = {
        'polymorphic_identity': 'domestic_customer',  # Define polymorphic identity for DomesticCustomer
    }


class ForeignCustomer(Customer):
    id = Column(Integer, ForeignKey('customer.id'), primary_key=True)
    passport_number = Column(String(20), nullable=False)  # Passport number
    country = Column(String(50), nullable=False)  # Nationality
    __mapper_args__ = {
        'polymorphic_identity': 'foreign_customer',  # Define polymorphic identity for ForeignCustomer
    }


hotel = Hotel(
    id=1,
    name="Luxury Hotel",
    address="112/Nguyen Van A"
)

room_statuses = [
    RoomStatus(name="Available"),
    RoomStatus(name="Booked"),
    RoomStatus(name="Checked"),
]
booking_statuses = [
    BookingStatus(name="Pending"),
    BookingStatus(name="Checked-in"),
    BookingStatus(name="Checked-out"),
    BookingStatus(name="Cancelled"),
]

rooms = [
    Room(
        id="101",
        name="Deluxe Room 101",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        hotel_id=1,  # Liên kết đến Hotel
        image="https://www.vietnambooking.com/wp-content/uploads/2021/02/khach-san-ho-chi-minh-28.jpg",
        size=30
    ),
    Room(
        id="102",
        name="Deluxe Room 102",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        hotel_id=1,  # Liên kết đến Hotel
        image="https://noithattugia.com/wp-content/uploads/2024/09/thiet-ke-noi-that-khach-san-kien-truc-noi-that-tu-gia-868.jpg",
        size=30
    ),
    Room(
        id="103",
        name="Deluxe Room 103",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        hotel_id=1,  # Liên kết đến Hotel
        image="https://saigontourist.com.vn/files/images/luu-tru/luu-tru-mien-nam/hotel-grand-saigon-2.jpg",
        size=45
    ),
    Room(
        id="104",
        name="Deluxe Room 104",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        hotel_id=1,  # Liên kết đến Hotel
        image="https://thietkethicong.org/Uploads/files/XLKHACHSAN/Newfolder4/ksty-23.jpg",
        size=30

    ), Room(
        id="105",
        name="Deluxe Room 105",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        hotel_id=1,  # Liên kết đến Hotel
        image="https://cf.bstatic.com/xdata/images/hotel/max1024x768/163589466.jpg?k=f6595e4f13c2a5f394598a838f3d92191e96af6098975642694351457f9669d4&o=&hp=1",
        size=30
    ), Room(
        id="106",
        name="Superior Room 106",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        hotel_id=1,  # Liên kết đến Hotel
        image="https://kientructayho.vn/wp-content/uploads/2020/12/mau-phong-khach-san-mini-dep-2.jpg",
        size=30
    )
]

room_types = [
    RoomType(name="Deluxe", price_per_night=150.0),
    RoomType(name="Suite", price_per_night=300.0),
    RoomType(name="Superior", price_per_night=450.0),
]

admin_user = User(
    name="admin",
    phone="0123456789",
    email="admin@example.com",
    address="Admin Address",
    type="user"
)
staff_user = Staff(
    name="staff01",
    phone="012924412",
    email="staff@example.com",
    address="Staff Address",
    type="staff"
)
user = Customer(
    name="user01",
    phone="0129244122",
    email="user@example.com",
    address="User Address",
    identification_number="0274834235305",
    type="customer"
)
# new_user = User(
#     name="hello",
#     email="adb123@"
# )
# new_cus = Customer(
#     name="hello",
#     email="adb123@",
#     type='customer'
# )
admin_account = Account(
    username="admin",
    password=str(hashlib.md5("1".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mã hóa
    role=AccountRole.ADMIN,  # Gán vai trò ADMIN
    user=admin_user  # Liên kết tài khoản với user
)
staff_account = Account(
    username="staff01",
    password=str(hashlib.md5("1".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mã hóa
    role=AccountRole.STAFF,  # Gán vai trò ADMIN
    user=staff_user  # Liên kết tài khoản với user
)
staff_account = Account(
    username="user01",
    password=str(hashlib.md5("1".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mã hóa
    role=AccountRole.USER,  # Gán vai trò ADMIN
    user=user  # Liên kết tài khoản với user
)
# new_account = Account(
#     username='HELLO',
#     password=str(hashlib.md5("admin".strip().encode('utf-8')).hexdigest()),
#     user =new_cus,  # Khóa ngoại
#     role=AccountRole.USER  # Mặc định là USER
# )
booking_rooms = [
    BookingRoom(
        room_id=101,
        staff_id=2,
        customer_id=3
    ),
    BookingRoom(
        room_id=102,
        staff_id=2,
        customer_id=3
    ),
    BookingRoom(
        room_id=105,
        staff_id=2,
        customer_id=3
    ),
    BookingRoom(
        room_id=106,
        staff_id=2,
        customer_id=3
    ),
    BookingRoom(
        room_id=101,
        staff_id=2,
        customer_id=3
    )
]
bills = [
    Bill(
        total_amount=700,
        booking_room_id=1,
    )
]

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(hotel)
        db.session.add_all(room_statuses)
        db.session.add_all(booking_statuses)
        db.session.add_all(room_types)
        db.session.add_all(rooms)
        db.session.add(admin_user)
        db.session.add(staff_user)
        db.session.add(user)
        db.session.add_all(booking_rooms)
        db.session.add_all(bills)
        db.session.commit()
