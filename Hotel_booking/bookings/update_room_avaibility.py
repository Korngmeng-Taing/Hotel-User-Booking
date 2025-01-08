from django.core.management.base import BaseCommand
from bookings.models import Booking
from datetime import date

class Command(BaseCommand):
    help = 'Update room availability based on checkout dates'

    def handle(self, *args, **kwargs):
        bookings = Booking.objects.filter(check_out__lt=date.today())
        updated_rooms = 0
        for booking in bookings:
            room = booking.room
            if not room.is_available:
                room.is_available = True
                room.save()
                updated_rooms += 1
        self.stdout.write(f"Updated availability for {updated_rooms} rooms.")
