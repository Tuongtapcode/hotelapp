from app.models import Room, RoomType, RoomStatus, User, Account, Customer, AccountRole, BookingRoom, Coefficient
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import current_user, logout_user
from flask import redirect, request
from wtforms.validators import DataRequired
from wtforms import SelectField
import dao
import random
from datetime import datetime


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        total_room = dao.count_room()
        data_available = {
            "available": dao.count_available_rooms(),  # Số phòng không có khách
            "total": total_room  # Tổng số phòng
        }
        room_guest_counts = dao.count_guests_per_room()
        # Lấy 5 hóa đơn gần nhất
        bill_recent_activities = dao.bill_recent_activities()
        room_capacity = dao.get_room_capacity()

        return self.render('admin/index.html', data_available=data_available, room_guest_counts=room_guest_counts,
                           bill_recent_activities=bill_recent_activities,room_capacity = room_capacity, total_room=total_room)


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


class CoefficientView(AdminView):
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True

class UserView(AdminView):
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True

class RoomView(AdminView):
    column_list = ['id', 'name', 'max_occupancy', 'room_type', 'room_status', 'size']
    form_columns = ['id', 'name', 'max_occupancy', 'room_type', 'room_status', 'size', 'image', 'hotel']
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True


class RoomTypeView(AdminView):
    column_list = ['id', 'name', 'rooms', 'price_per_night']
    form_columns = ['name', 'price_per_night']
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
        selected_month = request.args.get('month', default=datetime.now().month, type=int)
        selected_year = request.args.get('year', default=datetime.now().year, type=int)
        revenue_data = dao.revenue_by_day(selected_year, selected_month)
        revenue_roomtype_report_by_month = dao.revenue_roomtype_report_by_month(selected_year, selected_month)
        days_rented_in_month = dao.get_days_rented_in_month(year=selected_year,
                                                                                    month=selected_month)
        room_statistics = dao.get_room_statistics(year=selected_year, month=selected_month)
        return self.render(
            'admin/stats.html', revenue_data=revenue_data,
            current_year=datetime.now().year,
            selected_month=selected_month,
            selected_year=selected_year,
            revenue_roomtype_report_by_month=revenue_roomtype_report_by_month,
            days_rented_in_month=days_rented_in_month, room_statistics=room_statistics
        )


admin.add_view(RoomView(Room, db.session, name='Rooms'))
admin.add_view(RoomTypeView(RoomType, db.session, name='Room Types'))
admin.add_view(CustomerView(Customer, db.session, name='Customer'))
admin.add_view(UserView(User, db.session, name='User'))
admin.add_view(CoefficientView(Coefficient, db.session, name='Coefficient'))
admin.add_view(StatsView(name='Statistical'))
admin.add_view(LogoutView(name='Logout'))

# if __name__ == '__main__':
#     with app.app_context():
#         room_type = RoomType.query.first()
#         print(type(room_type.rooms))  # Kiểm tra kiểu dữ liệu
#         print(room_type.rooms)  # Xem dữ liệu cụ thể
