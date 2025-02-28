import random
import string
from django.core.management.base import BaseCommand
from relecloud.models import Destination, DestinationReview

class Command(BaseCommand):
    help = 'Generate random reviews for destinations'

    def handle(self, *args, **kwargs):
        destinations = Destination.objects.all()
        review_texts = [
            "Amazing experience!",
            "Would love to visit again.",
            "Not what I expected.",
            "Absolutely stunning!",
            "Could be better.",
            "Had a great time!",
            "The best trip ever!",
            "Not worth the money.",
            "A once in a lifetime experience.",
            "Highly recommended!",
            "Would not recommend.",
            "So much fun!",
            "An unforgettable journey filled with joy and adventure.",
            "A perfect getaway from the hustle and bustle of city life.",
            "The hospitality was top-notch, felt like home.",
            "A paradise on earth, truly mesmerizing.",
            "An overrated destination, not worth the hype.",
            "A hidden gem, exceeded all my expectations.",
            "The cultural experience was enriching and enlightening.",
            "A budget-friendly trip with priceless memories.",
            "The local cuisine was a delightful surprise.",
            "A disappointing trip, wouldn't recommend.",
            "A serene and peaceful retreat, just what I needed.",
            "An adventure-packed trip, full of thrills and excitement.",
            "The natural beauty of the place left me speechless.",
            "A perfect blend of relaxation and adventure.",
            "The tour guides were knowledgeable and friendly.",
            "An overpriced destination with mediocre attractions.",
            "A family-friendly destination with activities for all ages.",
            "The nightlife was vibrant and full of energy.",
            "A romantic getaway, perfect for couples.",
            "An eco-friendly destination, loved the sustainability efforts.",
            "The weather was perfect, couldn't have asked for more.",
            "A disappointing experience, wouldn't recommend.",
            "A luxurious trip, felt like royalty.",
            "The historical sites were fascinating and well-preserved.",
            "A memorable trip that I'll cherish forever.",
            "The local traditions and customs were intriguing.",
            "An affordable destination with plenty of free activities.",
            "The accommodations were comfortable and cozy.",
            "A tourist trap, avoid at all costs."
        ]

        for destination in destinations:
            for _ in range(random.randint(5, 150)):
                username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                rating = random.randint(1, 5)
                DestinationReview.objects.create(
                    destination=destination,
                    name=username,
                    rating=rating,
                    comment=random.choice(review_texts)
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated reviews for all destinations'))