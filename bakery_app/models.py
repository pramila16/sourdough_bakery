from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField, DecimalField, ListField, BooleanField
from datetime import datetime

class BakeryItem(Document):
    name = StringField(max_length=255, required=True)
    description = StringField()
    price = DecimalField(precision=2, required=True)
    quantity_in_stock = IntField(required=True)
    created_at = DateTimeField(default=datetime.utcnow, required=False)
    updated_at = DateTimeField(default=datetime.utcnow, onupdate=datetime.utcnow, required=False)
    is_deleted = BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.name} - {self.price}"

class BakingSchedule(Document):
    bakery_item = ReferenceField(BakeryItem, required=True)
    start_time = DateTimeField(default=datetime.utcnow)
    end_time = DateTimeField(default=datetime.utcnow)
    status = StringField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')
    quantity = IntField(required=True)
    created_at = DateTimeField(default=datetime.utcnow, required=False)
    updated_at = DateTimeField(default=datetime.utcnow, onupdate=datetime.utcnow, required=False)
    is_deleted = BooleanField(default=False)

    def __str__(self):
        return f"{self.bakery_item.name} scheduled from {self.start_time} to {self.end_time}"


class Ingredient(Document):
    name = StringField(max_length=255, required=True)
    quantity_in_stock = IntField(required=True)
    unit = StringField(max_length=20, required=True)
    created_at = DateTimeField(default=datetime.utcnow, required=False)
    updated_at = DateTimeField(default=datetime.utcnow, onupdate=datetime.utcnow, required=False)
    is_deleted = BooleanField(default=False)

    def __str__(self):
        return self.name


class Order(Document):
    customer_name = StringField(max_length=255, required=True)
    bakery_item_id = ReferenceField(BakeryItem, required=True)
    quantity = IntField(required=True)
    order_time = DateTimeField(default=datetime.utcnow, required=False)
    status = StringField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    version = IntField(default=1)
    created_at = DateTimeField(default=datetime.utcnow, required=False)
    updated_at = DateTimeField(default=datetime.utcnow, onupdate=datetime.utcnow, required=False)
    is_deleted = BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Order by {self.customer_name} for {self.bakery_item_id.name}"





