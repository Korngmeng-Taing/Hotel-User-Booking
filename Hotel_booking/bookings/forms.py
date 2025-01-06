from django import forms
from .models import Booking, Room
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    #This defines a new form class that inherits from UserCreationForm.
    # It is used for creating new users with additional fields 
    email = forms.EmailField(required=True)
    #adds an email field to the form ,making it a required field.
    class Meta:
        model = User
        #Specifies the model to use for the form.
        fields = ['username', 'email', 'password1', 'password2']
        #Specifies the fields to include in the form.
class BookingForm(forms.ModelForm):
     # This defines a new form class that inherits from ModelForm.
    # It is used for creating or updating Booking instances.
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_available=True),  # Show only available rooms
        #allows user to select from available rooms only
        empty_label="Select a Room",
        #sets the label for the empty choice in the dropdown
        widget=forms.Select(attrs={'class': 'form-select'})
        #adds a CSS class to the select element for styling
    )

    class Meta:
        model = Booking
        #specifies the model
        fields = ['room', 'check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        #Specifies custom widgets for the check-in and check-out fields to use date input types with specific CSS classes.
        #this widgets use html input element of type date and apply the form-control class for styling