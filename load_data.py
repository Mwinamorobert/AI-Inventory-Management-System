import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from core.models import Supplier, InventoryItem, Location
from django.contrib.auth.models import User

def load_data():
    # Clear existing data
    InventoryItem.objects.all().delete()
    Supplier.objects.all().delete()
    Location.objects.all().delete()

    # Create a test user
    user, _ = User.objects.get_or_create(username='admin', email='admin@example.com')
    user.set_password('admin123')
    user.save()

    # Create locations
    locations = ['Nairobi', 'Mombasa', 'Kisumu', 'Eldoret', 'Nakuru']
    for loc in locations:
        Location.objects.get_or_create(name=loc)

    # Load CSV
    df = pd.read_csv('datasets/inventory_data.csv')
    for _, row in df.iterrows():
        supplier, _ = Supplier.objects.get_or_create(name=row['supplier'])
        location = Location.objects.get(name=row['location'])
        InventoryItem.objects.create(
            name=row['name'],
            quantity=row['quantity'],
            price=row['price'],
            supplier=supplier,
            location=location,
            user=user
        )
    print("Data loaded successfully!")

if __name__ == "__main__":
    load_data()