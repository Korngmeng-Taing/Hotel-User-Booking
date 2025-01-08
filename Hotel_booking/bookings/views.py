from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from .forms import BookingForm, CustomUserCreationForm ,RoomForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, date
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .decoration import unauthenticated_user,allowed_user

@login_required
def room_list(request):
    """Update room availability dynamically and display all rooms."""
    today = date.today()
    bookings = Booking.objects.select_related('room').all()

    # Update room availability dynamically based on bookings
    for booking in bookings:
        room = booking.room
        if booking.check_in <= today <= booking.check_out:
            room.is_available = False
        else:
            room.is_available = True
        room.save()

    rooms = Room.objects.all()
    return render(request, 'bookings/room_list.html', {'rooms': rooms})

@login_required
def book_room(request):
    """Handle the room booking process."""
    room_id = request.GET.get('room_id')  # Get the room ID from the query string
    room = None

    # Ensure room exists if room_id is provided
    if room_id:
        room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        # Parse the dates
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect(f'/book?room_id={room_id}')  # Redirect with room_id
        # Prevent duplicate bookings
        if Booking.objects.filter(
            user=request.user,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date
        ).exists():
            messages.error(request, "You already have a booking for this room and date.")
            return redirect('my_bookings')
        # Create the booking if the room is valid
        if room:
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                check_in=check_in_date,
                check_out=check_out_date
            )
            room.is_available = False  # Mark the room as unavailable
            room.save()

            # Redirect to the booking confirmation page with query parameters
            url = reverse('booking_confirm', args=[room.id])
            query_string = f"?check_in={check_in_date}&check_out={check_out_date}"
            return HttpResponseRedirect(url + query_string)

    # Render the booking form with the room context
    return render(request, 'bookings/book_room.html', {'room': room})


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
            messages.success(request, "Booking confirmed!")
            return redirect('booking_success')

        elif 'cancel' in request.POST:
            # Delete the booking
            if Booking.objects.filter(room=room, check_out__gte=date.today()).exists():
                Booking.objects.filter(room=room, check_out__gte=date.today()).delete()
            
            # Check if the room is available after deleting the booking
            if not Booking.objects.filter(room=room, check_out__gte=date.today()).exists():
                room.is_available = True
                room.save()
            
            messages.success(request, f"Room {room.room_number} is now available.")
            return redirect('room_list')

    return render(request, 'bookings/booking_confirm.html', {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'total_cost': total_cost,
    })

@login_required
def booking_success(request):
    """Display the booking success page."""
    return render(request, 'bookings/booking_success.html')
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
@login_required
def admin_room_list(request):
    """Update room availability dynamically and display all rooms."""
    today = date.today()
    bookings = Booking.objects.select_related('room').all()

    # Update room availability dynamically based on bookings
    for booking in bookings:
        room = booking.room
        if booking.check_in <= today <= booking.check_out:
            room.is_available = False
        else:
            room.is_available = True
        room.save()

    rooms = Room.objects.all()
    return render(request, 'bookings/admin_room_list.html', {'rooms': rooms})
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')  # Redirect non-admins to the user dashboard
    return render(request, 'bookings/admin_dashboard.html')
def dashboard(request):
    rooms = Room.objects.all()  # Fetch all rooms for the slideshow
    context = {
        'rooms': rooms,
    }
    return render(request, 'bookings/dashboard.html', context)
@login_required
def admin_booking_list(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')  # Redirect non-admins
    bookings = Booking.objects.select_related('user', 'room').all()
    return render(request, 'bookings/admin_booking_list.html', {'bookings': bookings})
@login_required
def delete_room_admin(request, room_id):
    """
    Show a confirmation page before deleting the room.
    """
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        # If the request is POST, delete the room
        room.delete()
        return redirect('admin_room_list')  # Redirect to the admin room list after deletion

    # If the request is GET, show the confirmation page
    return render(request, 'bookings/delete_room.html', {'room': room})

@login_required
def update_room_admin(request, room_id):
    """
    Update room details.
    """
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room details updated successfully!")
            return redirect('admin_room_list')  # Redirect back to the admin room list
    else:
        form = RoomForm(instance=room)  # Prepopulate the form with the room details

    return render(request, 'bookings/update_room.html', {'form': form})

@login_required
def update_booking_admin(request, booking_id):
    """
    Update a booking's details by admin.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking details updated successfully!")
            return redirect('admin_booking_list')
    else:
        form = BookingForm(instance=booking)

    context = {
        'form': form,
        'booking': booking,  # Pass the booking object for room details
    }
    return render(request, 'bookings/update_booking.html', context)
@login_required
def delete_booking_admin(request, booking_id):
    """
    Delete a booking by admin.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        room = booking.room
        booking.delete()
        # Update room availability
        if not Booking.objects.filter(room=room, check_out__gte=date.today()).exists():
            room.is_available = True
            room.save()

        messages.success(request, "Booking deleted successfully!")
        return redirect('admin_booking_list')

    return render(request, 'bookings/delete_booking.html', {'booking': booking})

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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'bookings/login.html')

def logoutUser(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')
