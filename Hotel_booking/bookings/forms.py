from django import forms
from .models import Booking, Room
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
      
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        #Specifies the model to use for the form.
        fields = ['username', 'email' ,'password1', 'password2']
        #Specifies the fields to include in the form.

class BookingForm(forms.ModelForm):
    rooms_booked = forms.IntegerField(min_value=1,label='Number of rooms')
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out','rooms_booked']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'