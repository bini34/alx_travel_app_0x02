# alx_travel_app_0x00

## Milestone 2: Creating Models, Serializers, and Seeders

### Models
- `Listing`: Represents a property available for booking.
- `Booking`: Represents a booking made by a user for a listing.
- `Review`: Represents a review left by a user for a listing.

### Serializers
- `ListingSerializer`: Serializes Listing model data for API responses.
- `BookingSerializer`: Serializes Booking model data for API responses.

### Seeder
- Custom management command `seed` to populate the database with sample data for development and testing.

### Usage
- Run migrations: `python manage.py makemigrations && python manage.py migrate`
- Seed database: `python manage.py seed`

---

Copyright © 2025 ALX, All rights reserved.