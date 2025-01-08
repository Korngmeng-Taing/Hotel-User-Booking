from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('rooms/', views.room_list, name='room_list'),
    path('book/', views.book_room, name='book_room'),
    path('booking_confirm/<int:room_id>/', views.booking_confirm, name='booking_confirm'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('about-us/', views.about_us, name='about'),
    path('contact-us/', views.contact_us, name='contact'),
]
