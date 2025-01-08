from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from .forms import BookingForm, CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, date
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .decoration import unauthenticated_user


@login_required
def room_list(request):
    """Update room availability dynamically and display all rooms."""
    today = date.today()
    bookings = Booking.objects.all()

    # Update room availability dynamically based on bookings
    for booking in bookings:
        room = booking.room
        if booking.check_in <= today <= booking.check_out:
            room.is_available = False
        else:
            room.is_available = True
        room.save()

    rooms = Room.objects.all()  # Fetch all rooms
    return render(request, 'bookings/room_list.html', {'rooms': rooms})

@login_required
def book_room(request):
    """Handle the room booking process."""
    rooms = Room.objects.filter(is_available=True)  # Fetch only available rooms
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # Associate booking with the logged-in user
            booking.save()

            room = booking.room
            room.is_available = False  # Mark the room as unavailable
            room.save()

            # Redirect to booking confirmation page with query parameters
            url = reverse('booking_confirm', args=[room.id])
            query_string = f"?check_in={booking.check_in}&check_out={booking.check_out}"
            return HttpResponseRedirect(url + query_string)
    else:
        form = BookingForm()

    return render(request, 'bookings/book_room.html', {'form': form, 'rooms': rooms})

@login_required
def booking_confirm(request, room_id):
    """Confirm the booking details and process user actions."""
    room = get_object_or_404(Room, id=room_id)
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')

    # Validate check-in and check-out dates
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        messages.error(request, "Invalid check-in or check-out date.")
        return redirect('room_list')

    if check_out <= check_in:
        messages.error(request, "Check-out date must be after the check-in date.")
        return redirect('room_list')

    num_days = (check_out - check_in).days
    total_cost = num_days * room.price_per_night

    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Create a booking instance and mark the room as unavailable
            Booking.objects.create(
                user=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out
            )
            room.is_available = False
            room.save()
            return redirect('booking_success')
        elif 'cancel' in request.POST:
             # Mark the room as available if booking is canceled
            room.is_available = True
            room.save()
            messages.success(request, "Booking has been canceled.")
            return redirect('room_list')

    context = {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'total_cost': total_cost,
    }
    return render(request, 'bookings/booking_confirm.html', context)


@login_required
def booking_success(request):
    """Display the booking success page."""
    return render(request, 'bookings/booking_success.html')
@login_required
def delete_booking(request, booking_id):
    """Delete a booking and update room availability."""
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the logged-in user is authorized to delete the booking
    if booking.user != request.user:
        messages.error(request, "You are not authorized to delete this booking.")
        return redirect('room_list')

    room = booking.room
    booking.delete()  # Delete the booking

    # Update room availability
    if not Booking.objects.filter(room=room, check_out__gte=date.today()).exists():
        room.is_available = True
        room.save()

    messages.success(request, "Booking has been successfully deleted.")
    return redirect('room_list')
@login_required
def my_bookings(request):
    """Display the logged-in user's bookings."""
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    today = date.today()
    
    # Add status for each booking
    for booking in bookings:
        booking.status = "Active" if booking.check_out >= today else "Completed"

    context = {
        'bookings': bookings,
        'today': today,
        'year': today.year,
    }
    return render(request, 'bookings/my_bookings.html', context)
def dashboard(request):
    """Display the dashboard with all rooms."""
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'bookings/dashboard.html', context)

def about_us(request):
    """Display the 'About Us' page."""
    return render(request, 'bookings/about.html')

def contact_us(request):
    """Display the 'Contact Us' page."""
    return render(request, 'bookings/contact.html')

@unauthenticated_user
def registerPage(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'bookings/register.html', {'form': form})

@unauthenticated_user
def loginPage(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')  # Get the 'next' parameter from the URL
            return redirect(next_url if next_url else 'dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'bookings/login.html')

def logoutUser(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')
