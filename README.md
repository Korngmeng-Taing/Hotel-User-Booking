# Hotel Booking Web Application

Welcome to the **Hotel Booking Web Application**! This platform enables users to browse, book, and manage hotel rooms seamlessly. Admins can manage rooms and bookings efficiently, making it ideal for both customers and hotel staff.

---

## Future Work

-Payment Gateway Integration

## Features

### For Users:

- **Browse Rooms**: View available rooms with details such as price, capacity, and size.
- **Book Rooms**: Select check-in and check-out dates to book a room.
- **User Authentication**: Register, log in, and log out securely.
- **View Bookings**: Confirm or cancel bookings.

### For Admins:

- **Room Management**: Add, edit, and delete room details.
- **Booking Management**: View and manage all bookings.

---

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (default, can be switched to PostgreSQL or MySQL for production)
- **Libraries**: Flatpickr for date selection
- **Deployment**: (Optional)

---

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/hotel-booking.git
   cd hotel-booking
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate # Linux/macOS
   venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000`.

---

## Usage

### As a User:

1. **Register**: Create a new account on the registration page.
2. **Log In**: Access your dashboard using your credentials.
3. **Browse and Book**: View available rooms and book based on your preferences.
4. **Manage Bookings**: Confirm or cancel bookings.

### As an Admin:

1. Log in using admin credentials.
2. Access the admin panel at `http://127.0.0.1:8000/admin/`.
3. Manage rooms and bookings directly through the admin interface.

---

## Project Structure

main file

```plaintext
hotel-booking/
├── bookings/               # Core application logic
│   ├── templates/bookings/ # HTML templates
│   ├── static/css/         # CSS files
│   ├── views.py            # View functions
│   ├── models.py           # Database models
│   ├── forms.py            # Django forms
├── upload/media            # upload images
├── manage.py               # Django management script
└── README.md               # Project documentation
```

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Django for the robust framework.
- Bootstrap for the responsive design.
- Flatpickr for date selection functionality.
