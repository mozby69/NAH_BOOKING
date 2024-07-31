from django.urls import path
from . import views
from myapp.nah_booking_backend.index import index
from .nah_booking_backend import pspmi_booking











urlpatterns = [
    path('', views.login_view, name='login'),
    path('index/', index, name="index"),
    path('logout/', views.custom_logout, name='logout'),
    path('pspmi_main_page/',pspmi_booking.pspmi_main_page, name="pspmi_main_page"),
    path('save_event/', pspmi_booking.save_event, name='save_event'),
    path('get_events/', pspmi_booking.get_events, name='get_events'),
    path('update_event',pspmi_booking.update_event, name="update_event"),
    path('get_event_details',pspmi_booking.get_event_details, name="get_event_details"),
    path('delete_event',pspmi_booking.delete_event, name="delete_event"),
    path('pspmi_view_page/',pspmi_booking.pspmi_view_page, name="pspmi_view_page"),
    path('pspmi_weekly/', pspmi_booking.pspmi_monthly_page, name="pspmi_monthly_page"),
    path('drag_update/',pspmi_booking.drag_update, name="drag_update"),
    path('pspmi_yearly_page/',pspmi_booking.pspmi_yearly_page, name="pspmi_yearly_page"),
    path('notify_booking/', pspmi_booking.notify_booking, name="notify_booking"),
    path('booking_reports/', pspmi_booking.booking_reports, name="booking_reports"),
    path('pspmi_print_page/', pspmi_booking.pspmi_print_page, name="pspmi_print_page"),
    path('print_monthly/', pspmi_booking.print_monthly, name="print_monthly"),

]