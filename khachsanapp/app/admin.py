from app.models import Room, RoomPrice, RoomType, RoomStatus, User, Account, Customer, AccountRole, BookingRoom
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from flask_login import current_user, logout_user
from flask import redirect
from wtforms.validators import DataRequired
from wtforms import SelectField
from wtforms_sqlalchemy.fields import QuerySelectField

admin = Admin(app=app, name='Hotel Management', template_mode='bootstrap4')


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.__eq__(AccountRole.ADMIN)


# class RoomView(AdminView):
#     column_list = ['id', 'name', 'max_occupancy', 'room_type_id', 'room_status_id',
#                    'room_price_id', 'hotel_id', 'size']
#     form_columns = ['name', 'room_type_id', 'room_status_id', 'room_price_id', 'hotel_id', 'size']
#     can_export = True
#     can_create = True
#     can_edit = True
#     can_delete = True
#
#     def scaffold_form(self):
#         form_class = super().scaffold_form()
#
#         with app.app_context():
#             # Sử dụng QuerySelectField với query_factory
#             form_class.room_type_id = QuerySelectField(
#                 'Room Type',
#                 query_factory=lambda: RoomType.query.all(),  # Phải trả về danh sách các object
#                 get_label='name',  # Tên thuộc tính để hiển thị
#                 allow_blank=True  # Cho phép giá trị rỗng
#             )
#             form_class.room_status_id = QuerySelectField(
#                 'Room Status',
#                 query_factory=lambda: RoomStatus.query.all(),
#                 get_label='name',
#                 allow_blank=True
#             )
#             form_class.room_price_id = QuerySelectField(
#                 'Room Price',
#                 query_factory=lambda: RoomPrice.query.all(),
#                 get_label=lambda rp: f"${rp.price_per_night:.2f}",
#                 allow_blank=True
#             )
#
#         return form_class


class RoomView(AdminView):
    column_list = ['id', 'name', 'max_occupancy', 'room_type.name', 'room_status.name', 'room_price.price_per_night',
                   'hotel_id', 'size']
    form_columns = ['name', 'max_occupancy', 'room_type', 'room_status', 'room_price', 'hotel_id', 'image', 'size']
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    



class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class RoomTypeView(AdminView):
    column_list = ['name', 'rooms']  # Show name and linked rooms
    form_columns = ['name']  # Allow admin to edit name


class RoomPriceView(AdminView):
    column_list = ['price_per_night', 'rooms']  # Show price and linked rooms
    form_columns = ['price_per_night']  # Allow admin to edit price


class UserView(AdminView):
    column_list = ['id', 'type', 'name', 'phone']  # Show price and linked rooms


class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')


admin.add_view(RoomPriceView(RoomPrice, db.session, name='Room Prices'))
admin.add_view(RoomTypeView(RoomType, db.session, name='Room Types'))
admin.add_view(UserView(User, db.session, name='User'))
admin.add_view(RoomView(Room, db.session, name='Rooms'))
admin.add_view(StatsView(name='Statistical'))
admin.add_view(LogoutView(name='Logout'))
