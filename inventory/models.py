from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- Master Tables ---

class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    department = models.CharField(max_length=50, null=True)
    position = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}'s contact person - {self.contact_person}"

class Category(models.Model):
    categories = [
        ('power_tools', 'Power Tools'),
        ('hand_tools', 'Hand Tools'),
        ('fasteners', 'Fasteners & Fixings'),
        ('electrical', 'Electrical Components'),
        ('plumbing', 'Plumbing & Piping'),
        ('building_materials', 'Building Materials'),
        ('adhesives', 'Adhesives & Sealants'),
        ('paints', 'Paints & Finishes'),
        ('safety_ppe', 'Safety Equipment & PPE'),
        ('fittings', 'Hardware Fittings'),
        ('abrasives', 'Abrasives & Consumables'),
        ('hvac', 'HVAC & Ventilation'),
        ('garden', 'Garden & Outdoor'),
        ('storage', 'Storage & Organization'),
        ('machinery', 'Machinery & Equipment'), 
    ]
    category_id = models.CharField(max_length=421, unique=True, null=True)
    category_name = models.CharField(max_length=25, choices=categories, default='paints')


    def __str__(self):
        for category in self.categories:
            if self.category_name == category[0]:
                return category[1]  # Return the display name
        return self.category_name 

class Item(models.Model):
    item_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    warrenty = models.DateField(null=True,blank=True,help_text="Warrenty Expire Date, if available")
    default_unit_of_measure = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.name} ({self.item_code})"


# --- Transaction Tables ---

class Purchase(models.Model):
    purchase_no = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    purchase_date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Calculate total cost
        self.total_cost = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # Update stock automatically
        self.item.current_stock += self.quantity
        self.item.save()

    def __str__(self):
        return f"Purchase {self.purchase_no} - {self.item.name} -- {Item.objects.all()}"
   
class Project(models.Model):
    project_name = models.CharField(max_length=100)
    responsible_person = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project_name}'

class Issue(models.Model):
    utilize_no = models.CharField(max_length=20, unique=True)
    issued_to = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    issue_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Issue {self.utilize_no} - {self.issued_to.first_name}"
    

class IssueItem(models.Model):
    issue = models.ForeignKey(Issue, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_issued = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Decrease stock automatically
        if self.item.current_stock >= self.quantity_issued:
            self.item.current_stock -= self.quantity_issued
            self.item.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError(f"Not enough stock for item {self.item.name}")

    def __str__(self):
        return f"{self.item.name} x {self.quantity_issued}"

