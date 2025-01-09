from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.core.exceptions import ValidationError

class Room(models.Model):
    ROOM_TYPES = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES)
    price_per_night = models.IntegerField()
    is_available = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField()
    size = models.IntegerField()
    image = models.ImageField(upload_to='upload/media/', blank=True, null=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    def clean(self):
        # Ensure check-out is after check-in
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")

    def __str__(self):
        return f"Booking: {self.user.username} - {self.room.room_number} ({self.check_in} to {self.check_out})"

@receiver(post_save, sender=Booking)
def update_room_availability(sender, instance, **kwargs):
    room = instance.room
    if instance.check_out < date.today():  # If the checkout date is in the past
        room.is_available = True
    else:  # If there is a future or current booking
        room.is_available = False
    room.save()