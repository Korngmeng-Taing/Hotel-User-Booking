from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from .forms import BookingForm, CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
@login_required #requires user to be logged in to access the view
def room_list(request):
    rooms = Room.objects.all() # Fetch all rooms from the database
    return render(request, 'bookings/room_list.html', {'rooms': rooms})
@login_required
def book_room(request):
    rooms = Room.objects.filter(is_available=True)  # Fetch available rooms only
    #filter available rooms only
    if request.method == 'POST':#check if the request method is POST(form submission)

        form = BookingForm(request.POST)# Create a form instance with the submitted data
        if form.is_valid():
            booking = form.save(commit=False)# create a booking instance but don't save it yet
            room = booking.room #get room associated with the booking
            check_in = request.POST.get('check_in') #get check_in date from the form
            check_out = request.POST.get('check_out')

            # Redirect to booking_confirm with query parameters
            url = reverse('booking_confirm', args=[room.id])
            #create the query string with check_in and check_out dates
            query_string = f"?check_in={check_in}&check_out={check_out}"
            return HttpResponseRedirect(url + query_string)
    else:
        form = BookingForm() # Create an empty form instance

    return render(request, 'bookings/book_room.html', {'form': form, 'rooms': rooms})
@login_required
def booking_confirm(request, room_id):
    room = get_object_or_404(Room, id=room_id) 
    # Get the room object based on the room_id from the URL
    check_in_str = request.GET.get('check_in')  # get check_in as a string from the query string
    check_out_str = request.GET.get('check_out')  # Retrieve check_out as a string

    try:
        # Convert the strings to datetime.date objects
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        # Handle invalid date format or missing date
        messages.error(request, "Invalid check-in or check-out date.")
        return redirect('room_list')
     # Calculate total cost
    num_days = (check_out - check_in).days
    total_cost = num_days * room.price_per_night

    if request.method == 'POST':
        if 'confirm' in request.POST: #if user confirm the booking ,a new booking instance is created
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out
            )
            room.is_available = False # Mark the room as unavailable
            room.save() # Save the changes
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


def registerPage(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): #check if it valid
            form.save() #save the new user to databases
            username = form.cleaned_data.get('username') #get the username from the form
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'bookings/register.html', {'form': form})


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        #Authenticates the user with the provided username and password
        if user is not None: #Checks if the user object is not None, meaning the authentication was successful.
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'bookings/login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')
