from app.models import Room, RoomType, RoomStatus, User, Account, Customer, AccountRole, BookingRoom, hotel
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import current_user, logout_user
from flask import redirect
from wtforms.validators import DataRequired
from wtforms import SelectField
import dao
import random

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        data = {
            "available": dao.count_available_rooms(),  # Số phòng không có khách
            "total": dao.count_room()  # Tổng số phòng
        }
        room_guest_counts = dao.count_guests_per_room()
        return self.render('admin/index.html', data=data, room_guest_counts=room_guest_counts)


admin = Admin(app=app, name='Hotel Management', template_mode='bootstrap4', index_view=MyAdminIndexView())


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.__eq__(AccountRole.ADMIN)


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class RoomView(AdminView):
    column_list = ['id', 'name', 'max_occupancy', 'room_type', 'room_status', 'size']
    form_columns = ['id', 'name', 'max_occupancy', 'room_type', 'room_status', 'size', 'image', 'hotel']
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True


class RoomTypeView(AdminView):
    column_list = ['id', 'name', 'rooms', 'price_per_night']
    form_columns = ['name','price_per_night' ]
    can_edit = True
    def _format_rooms(view, context, model, name):
        return ', '.join([room.name for room in model.rooms]) if model.rooms else 'No rooms'

    column_formatters = {
        'rooms': _format_rooms
    }



class CustomerView(AdminView):
    form_columns = ['name', 'phone', 'email', 'address', 'type']


class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        revenue_data = [
            {"month": "January", "revenue": random.randint(5000, 20000)},
            {"month": "February", "revenue": random.randint(5000, 20000)},
            {"month": "March", "revenue": random.randint(5000, 20000)},
            {"month": "April", "revenue": random.randint(5000, 20000)},
            {"month": "May", "revenue": random.randint(5000, 20000)},
            {"month": "June", "revenue": random.randint(5000, 20000)},
            {"month": "July", "revenue": random.randint(5000, 20000)},
            {"month": "August", "revenue": random.randint(5000, 20000)},
            {"month": "September", "revenue": random.randint(5000, 20000)},
            {"month": "October", "revenue": random.randint(5000, 20000)},
            {"month": "November", "revenue": random.randint(5000, 20000)},
            {"month": "December", "revenue": random.randint(5000, 20000)},
        ]

        # Dữ liệu giả cho tần suất sử dụng loại phòng
        usage_data = [
            {"room_type": "Deluxe", "usage_count": random.randint(20, 50)},
            {"room_type": "Suite", "usage_count": random.randint(10, 30)},
            {"room_type": "Standard", "usage_count": random.randint(30, 60)},
            {"room_type": "Family", "usage_count": random.randint(5, 15)},
        ]

        return self.render(
            'admin/stats.html',
            revenue_data=revenue_data,
            usage_data=usage_data,
        )


admin.add_view(RoomView(Room, db.session, name='Rooms'))
admin.add_view(RoomTypeView(RoomType, db.session, name='Room Types'))
admin.add_view(CustomerView(Customer, db.session, name='Customer'))

admin.add_view(StatsView(name='Statistical'))
admin.add_view(LogoutView(name='Logout'))

# if __name__ == '__main__':
#     with app.app_context():
#         room_type = RoomType.query.first()
#         print(type(room_type.rooms))  # Kiểm tra kiểu dữ liệu
#         print(room_type.rooms)  # Xem dữ liệu cụ thể
