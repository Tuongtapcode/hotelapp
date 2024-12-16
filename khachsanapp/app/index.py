from sqlalchemy.orm import query_expression
import dao
from flask import render_template, request, redirect, session, flash, url_for
from app import app, db, login
from flask_login import login_user, logout_user
from app.models import AccountRole, Account, User, Room, Customer
from datetime import datetime, date
from flask_login import current_user


@app.route('/')
def index():
    rooms = dao.load_rooms()
    return render_template('index.html', rooms=rooms)


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Kiểm tra thông tin tài khoản trong DAO
        account = dao.auth_account(username=username, password=password)
        if account:
            session['account_id'] = account.id
            session['user_id'] = account.user.id  # Lưu user_id vào session
            session['role'] = account.role.name  # Lưu vai trò (ADMIN, STAFF, USER)
            login_user(account)  # Sử dụng Flask-Login để quản lý phiên đăng nhập
            return redirect('/')
        else:
            flash('Invalid username or password!', 'error')  # Gửi thông báo lỗi
    return render_template('login.html')  # Render trang đăng nhập


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_account(username=username, password=password, role=AccountRole.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/')


@app.route("/register", methods=['get', 'post'])
def register_process():
    err_msg = None
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        full_name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        terms = request.form.get('terms')

        if password != confirm_password:
            flash('You must accept the terms and conditions!', 'error')
            return render_template('register.html')

        existing_user = Account.query.filter_by(username=username).first()

        if existing_user:
            flash(f"Username '{username}' is already taken! Please choose another.", 'error')
            return render_template('register.html')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash(f"Email '{email}' is already registered! Please use another.", 'error')
            return render_template('register.html')

        if dao.add_user_account(full_name, email, username, password):
            flash('Registration successful! You can now login.', 'success')
            return redirect('/login')

    return render_template('register.html', err_msg=err_msg)


@app.route('/search', methods=['GET'])
def search():
    room_type_id = request.args.get("room_type_id")
    max_occupancy = request.args.get('max_occupancy', type=int)
    max_occupancy = request.args.get('max_occupancy', type=int)
    room_price = request.args.get('price', type=float)
    rooms = dao.search_rooms_direct(room_type_id, max_occupancy, room_price, 1, None)
    return render_template('rooms.html', rooms=rooms)


@app.route('/book-room', methods=['POST'])
def book_room():
    today = date.today().strftime('%Y-%m-%d')
    # Kiểm tra người dùng đã đăng nhập
    if not current_user.is_authenticated:
        flash('Bạn cần đăng nhập trước khi đặt phòng!', 'error')
        return redirect('/login')  # Chuyển hướng về trang đăng nhập
    room_id = request.form['room_id']
    room = Room.query.get(room_id)
    # Lấy thông tin khách hàng từ session
    account = current_user
    user = account.user
    return render_template('book_room.html', room=room, user=user, today=today)


@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    # Lấy dữ liệu từ form
    room_id = request.form.get('room_id')
    user_id = request.form.get('user_id')
    checkin_str = request.form.get('checkin')
    checkout_str = request.form.get('checkout')
    # Chuyển đổi ngày giờ từ chuỗi sang đối tượng datetime
    checkin = datetime.strptime(checkin_str, '%Y-%m-%dT%H:%M')
    checkout = datetime.strptime(checkout_str, '%Y-%m-%dT%H:%M')
    # Kiểm tra phòng và người dùng
    room = Room.query.get(room_id)
    customer = Customer.query.get(user_id)
    booking = dao.create_booking(room, None, customer, checkin, checkout)
    flash('Đặt phòng thành công!', 'success')
    return render_template('confirm-booking.html', booking=booking, room=room, customer=customer)


@login.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


# @app.before_request
# def restrict_admin_access():
#     # Kiểm tra nếu đường dẫn bắt đầu bằng /admin
#     if request.path.startswith('/admin'):
#         if not (current_user.is_authenticated and current_user.role == AccountRole.ADMIN):
#             return redirect('/login')


def is_logged_in():
    return 'id' in session


if __name__ == '__main__':
    from app import admin
    from app.staff import staff_bp  # Ensure correct import

    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.run(debug=True)
