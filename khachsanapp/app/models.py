from email.mime import image
import hashlib
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship, backref
from app import app, db
from enum import Enum as RoleEnum
from flask_login import UserMixin, LoginManager
from datetime import datetime


class AccountRole(RoleEnum):
    ADMIN = 1
    STAFF = 2
    USER = 3


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

    __mapper_args__ = {
        'polymorphic_identity': 'customer',  # Set polymorphic identity for Customer
    }


class RoomStatus(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    rooms = relationship("Room", backref="room_status", lazy=True)

    def __str__(self):
        return self.name


class RoomPrice(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    price_per_night = Column(Float, nullable=False)
    rooms = relationship("Room", backref="room_price", lazy=True)

    def __str__(self):
        return str(self.price_per_night)


class RoomType(db.Model):
    # __tablename__ = 'RoomType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    rooms = relationship("Room", backref="room_type", lazy=True)

    def __str__(self):
        return self.name


class Room(db.Model):
    id = Column(String(10), primary_key=True)
    name = Column(String(50), unique=True)
    max_occupancy = Column(Integer)
    room_type_id = Column(Integer, ForeignKey('room_type.id'), nullable=False)
    room_status_id = Column(Integer, ForeignKey('room_status.id'), nullable=False)
    room_price_id = Column(Integer, ForeignKey('room_price.id'), nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)
    rooms_booking = relationship('BookingRoom', backref='BookingRoom', lazy=True)
    image = Column(String(200), nullable=False)
    size = Column(Float)


class BookingRoom(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_day = Column(DateTime, nullable=False, unique=True)
    checkin = Column(DateTime, nullable=False)
    checkout = Column(DateTime, nullable=False)
    room_id = Column(String(10), ForeignKey('room.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    bill = relationship("Bill", back_populates="booking_room", uselist=False)


class Hotel(db.Model):
    # __tablename__ = 'hotel'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # Hotel name
    address = Column(String(200), nullable=False)
    rooms = relationship('Room', backref='hotel', cascade="all, delete-orphan")


class Staff(db.Model):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    rooms_booking = relationship('BookingRoom', backref='staff', lazy=True)


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


class Bill(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_amount = Column(Float, nullable=False)  # Tổng số tiền hóa đơn
    issue_date = Column(DateTime, nullable=False)  # Ngày tạo hóa đơn
    booking_room_id = Column(Integer, ForeignKey('booking_room.id'), nullable=False)  # Liên kết đến đặt phòng
    booking_room = relationship("BookingRoom", back_populates="bill")  # Quan hệ với BookingRoom
    payment = relationship("Payment", back_populates="bill", uselist=False)


class Payment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)  # Số tiền thanh toán
    payment_date = Column(DateTime, nullable=False)  # Ngày thanh toán
    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=False, unique=True)  # Liên kết đến hóa đơn (1-1)
    bill = relationship("Bill", back_populates="payment")


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

room_prices = [
    RoomPrice(price_per_night=150.0),
    RoomPrice(price_per_night=300.0),
    RoomPrice(price_per_night=450.0),
]
rooms = [
    Room(
        id="101",
        name="Deluxe Room 101",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        room_price_id=2,  # Liên kết đến RoomPrice
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
        room_price_id=2,  # Liên kết đến RoomPrice
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
        room_price_id=2,  # Liên kết đến RoomPrice
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
        room_price_id=2,  # Liên kết đến RoomPrice
        hotel_id=1,  # Liên kết đến Hotel
        image="https://thietkethicong.org/Uploads/files/XLKHACHSAN/Newfolder4/ksty-23.jpg",
        size=30

    ), Room(
        id="105",
        name="Deluxe Room 105",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        room_price_id=2,  # Liên kết đến RoomPrice
        hotel_id=1,  # Liên kết đến Hotel
        image="https://cf.bstatic.com/xdata/images/hotel/max1024x768/163589466.jpg?k=f6595e4f13c2a5f394598a838f3d92191e96af6098975642694351457f9669d4&o=&hp=1",
        size=30
    ), Room(
        id="106",
        name="Superior Room 106",
        max_occupancy=2,
        room_type_id=1,  # Liên kết đến RoomType
        room_status_id=1,  # Liên kết đến RoomStatus
        room_price_id=2,  # Liên kết đến RoomPrice
        hotel_id=1,  # Liên kết đến Hotel
        image="https://kientructayho.vn/wp-content/uploads/2020/12/mau-phong-khach-san-mini-dep-2.jpg",
        size=30
    )
]
room_types = [
    RoomType(name="Deluxe"),
    RoomType(name="Suite"),
    RoomType(name="Superior"),
]

admin_user = User(
    name="admin",
    phone="0123456789",
    email="admin@example.com",
    address="Admin Address",
    type="user"
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
    password=str(hashlib.md5("admin".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mã hóa
    role=AccountRole.ADMIN,  # Gán vai trò ADMIN
    user=admin_user  # Liên kết tài khoản với user
)
# new_account = Account(
#     username='HELLO',
#     password=str(hashlib.md5("admin".strip().encode('utf-8')).hexdigest()),
#     user =new_cus,  # Khóa ngoại
#     role=AccountRole.USER  # Mặc định là USER
# )
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(hotel)
        db.session.add_all(room_statuses)
        db.session.add_all(room_prices)
        db.session.add_all(room_types)
        db.session.add_all(rooms)
        db.session.add(admin_user)

        db.session.commit()
