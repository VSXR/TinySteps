import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from tinySteps.models import Guides_Model, Category_Model

class Command(BaseCommand):
    help = 'Generates random nutrition guides'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of guides to generate')
        parser.add_argument('--clear', action='store_true', help='Delete existing guides before creating new ones')
        parser.add_argument('--approved', action='store_true', help='Create guides as approved')

    def handle(self, *args, **kwargs):
        count = kwargs.get('count', 5)
        clear = kwargs.get('clear', False)
        approved = kwargs.get('approved', False)
        
        # Verify there are users in the system
        users = list(User.objects.filter(is_staff=True)) or list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users in the database. Create some first.'))
            return
        
        # Verify there are categories
        categories = list(Category_Model.objects.all())
        if not categories:
            self.stdout.write(self.style.WARNING('No categories defined. Creating default category.'))
            category = Category_Model.objects.create(name="Child Nutrition", description="Guides on food for babies and children")
            categories = [category]
        
        # Delete existing guides if requested
        if clear:
            confirm = input("Are you sure you want to delete ALL nutrition guides? (y/n): ").lower()
            if confirm == 'y':
                Guides_Model.objects.filter(guide_type='nutrition').delete()
                self.stdout.write(self.style.SUCCESS('All existing nutrition guides have been deleted'))
            else:
                self.stdout.write(self.style.WARNING('Operation canceled by user'))
        
        # Common topics for nutrition guides
        topics = [
            "Introduction to", "Complete guide to", "Tips for", "Importance of",
            "How to prepare", "Benefits of", "Best options for", "Plan for",
            "Essential nutrients in", "Healthy alternatives to"
        ]
        
        subjects = [
            "complementary feeding", "first solid foods", "homemade baby food", 
            "stage-based feeding", "fruits and vegetables for babies", "proteins for children", 
            "food allergies", "healthy snacks", "feeding preschoolers",
            "child hydration", "vitamins and minerals", "feeding during illness"
        ]
        
        # Text for descriptions (detailed guide content)
        intro_texts = [
            "Nutrition is fundamental for your child's proper development. In this guide, we explain everything you need to know about {}.",
            "Many parents wonder how to approach {}. This guide offers all the necessary information in a clear and simple way.",
            "Providing adequate nutrition is essential for healthy growth. Learn all about {} with our evidence-based recommendations."
        ]
        
        main_content = [
            "## Why is it important?\n\nGood nutrition during childhood builds the foundation for healthy habits throughout life. The first years are crucial for your child's physical and cognitive development.\n\n",
            "## Age-based recommendations\n\n**0 to 6 months:** Exclusive breastfeeding or infant formula.\n\n**6 to 12 months:** Gradual introduction of solid foods while maintaining breastfeeding or formula.\n\n**1 to 3 years:** Diet diversification with all food groups.\n\n",
            "## Practical advice\n\n1. Introduce one new food at a time and wait 3-5 days before introducing another.\n2. Offer nutritious foods in small portions.\n3. Avoid adding salt or sugar to baby foods.\n4. Create a positive environment during meals, without pressuring the child.\n\n",
            "## Recommended foods\n\n* Fruits: apple, pear, banana, melon (adapted according to age)\n* Vegetables: carrot, pumpkin, potato, peas\n* Cereals: rice, oats, pasta (gluten-free for children under 1 year)\n* Proteins: chicken, white fish, well-cooked legumes, egg\n\n",
            "## Foods to avoid\n\n* Honey for children under 1 year (risk of botulism)\n* Cow's milk as a main drink before one year\n* Whole nuts before 4-5 years (choking hazard)\n* Processed foods with high content of salt, sugar, or additives\n\n"
        ]
        
        conclusion_texts = [
            "Remember that each child is different, and it's important to adapt these recommendations to your child's individual needs. Always consult with a pediatrician if you have any questions about your little one's nutrition.",
            "Maintain a positive attitude towards food and be a good example for your child. The healthy eating habits established now will have a lasting impact on their life.",
            "Patience is key in the child feeding process. Some children need to try a food up to 15 times before accepting it. Don't get discouraged and continue offering healthy and varied options."
        ]
        
        # Tags for nutrition guides
        all_tags = [
            "child nutrition", "baby feeding", "first foods", "baby food", 
            "proteins", "vitamins", "minerals", "fruits", "vegetables", "cereals", 
            "complementary feeding", "breastfeeding", "formula", "food allergies", 
            "healthy snacks", "development", "growth", "hydration"
        ]
        
        # Create nutrition guides
        created_count = 0
        now = timezone.now()
        
        for i in range(count):
            try:
                # Create random title
                topic = random.choice(topics)
                subject = random.choice(subjects)
                title = f"{topic} {subject}"
                if len(title) > 100:
                    title = title[:97] + "..."
                
                # Create structured description
                intro = random.choice(intro_texts).format(subject)
                content_sections = random.sample(main_content, k=min(4, len(main_content)))
                conclusion = random.choice(conclusion_texts)
                
                desc = intro + "\n\n" + "".join(content_sections) + conclusion
                
                # Select random tags (3-6 tags)
                num_tags = random.randint(3, 6)
                tags = ", ".join(random.sample(all_tags, k=min(num_tags, len(all_tags))))
                
                # Select random category
                category = random.choice(categories)
                
                # Select random author
                author = random.choice(users)
                
                # Determine status and dates
                status = 'approved' if approved else random.choice(['pending', 'approved', 'approved'])  # Higher probability of approved
                days_ago = random.randint(0, 180)  # Guide created between today and 180 days ago
                created_at = now - timedelta(days=days_ago, 
                                           hours=random.randint(0, 23),
                                           minutes=random.randint(0, 59))
                
                # If approved, set approval date
                approved_at = None
                if status == 'approved':
                    approved_days_ago = random.randint(0, days_ago)  # Approved after creation
                    approved_at = now - timedelta(days=approved_days_ago,
                                                hours=random.randint(0, 23),
                                                minutes=random.randint(0, 59))
                
                # Create the guide
                guide = Guides_Model.objects.create(
                    title=title,
                    desc=desc,
                    guide_type='nutrition',
                    tags=tags,
                    category=category,
                    author=author,
                    status=status,
                    created_at=created_at,
                    approved_at=approved_at
                )
                
                created_count += 1
                self.stdout.write(f"Created nutrition guide: {title} ({status})")
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating nutrition guide: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} nutrition guides have been created'))