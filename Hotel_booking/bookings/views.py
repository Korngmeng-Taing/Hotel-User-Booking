from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from .forms import BookingForm, CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .decoration import unauthenticated_user, allowed_user

@login_required  # Requires user to be logged in to access this view
def room_list(request):
    rooms = Room.objects.all()  # Fetch all rooms from the database
    return render(request, 'bookings/room_list.html', {'rooms': rooms})

@login_required
def book_room(request):
    rooms = Room.objects.filter(is_available=True)  # Fetch available rooms only
    if request.method == 'POST':  # Check if the request method is POST (form submission)
        form = BookingForm(request.POST)  # Create a form instance with the submitted data
        if form.is_valid():
            booking = form.save(commit=False)  # Create a booking instance but don't save it yet
            room = booking.room  # Get room associated with the booking
            check_in = request.POST.get('check_in')  # Get check-in date from the form
            check_out = request.POST.get('check_out')

            # Redirect to booking_confirm with query parameters
            url = reverse('booking_confirm', args=[room.id])
            query_string = f"?check_in={check_in}&check_out={check_out}"
            return HttpResponseRedirect(url + query_string)
    else:
        form = BookingForm()  # Create an empty form instance

    return render(request, 'bookings/book_room.html', {'form': form, 'rooms': rooms})

@login_required
def booking_confirm(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    check_in_str = request.GET.get('check_in')  # Get check-in as a string from the query string
    check_out_str = request.GET.get('check_out')  # Retrieve check-out as a string

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        messages.error(request, "Invalid check-in or check-out date.")
        return redirect('room_list')

    num_days = (check_out - check_in).days
    total_cost = num_days * room.price_per_night

    if request.method == 'POST':
        if 'confirm' in request.POST:  # If user confirms booking, create a booking instance
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out
            )
            room.is_available = False  # Mark the room as unavailable
            room.save()  # Save changes
            return redirect('booking_success')
        elif 'cancel' in request.POST:
            return redirect('room_list')

    context = {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'total_cost': total_cost,
        'user': request.user,
    }
    return render(request, 'bookings/booking_confirm.html', context)

@login_required
def booking_success(request):
    return render(request, 'bookings/booking_success.html')

def dashboard(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'bookings/dashboard.html', context)

def about_us(request):
    return render(request, 'bookings/about.html')

def contact_us(request):
    return render(request, 'bookings/contact.html')

@unauthenticated_user  # Redirect authenticated users trying to access register page
def registerPage(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():  # Check if it is valid
            form.save()  # Save the new user to the database
            username = form.cleaned_data.get('username')  # Get the username from the form
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'bookings/register.html', {'form': form})

@unauthenticated_user  # Redirect authenticated users trying to access login page
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:  # Successful authentication
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'bookings/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')
