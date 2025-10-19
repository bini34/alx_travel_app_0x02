from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews.'

    def handle(self, *args, **kwargs):
        # Create users
        users = []
        for i in range(5):
            username = f'user{i+1}'
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            users.append(user)

        # Create listings
        listings = []
        for i in range(10):
            listing, created = Listing.objects.get_or_create(
                title=f'Listing {i+1}',
                defaults={
                    'description': f'Description for listing {i+1}',
                    'price': random.uniform(50, 500),
                    'location': f'City {i+1}',
                    'owner': random.choice(users),
                }
            )
            listings.append(listing)

        # Create bookings
        for i in range(15):
            listing = random.choice(listings)
            user = random.choice(users)
            start_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(1, 7))
            Booking.objects.get_or_create(
                listing=listing,
                user=user,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'guests': random.randint(1, 5),
                }
            )

        # Create reviews
        for i in range(20):
            listing = random.choice(listings)
            user = random.choice(users)
            Review.objects.get_or_create(
                listing=listing,
                user=user,
                defaults={
                    'rating': random.randint(1, 5),
                    'comment': f'Review {i+1} for {listing.title}',
                }
            )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))