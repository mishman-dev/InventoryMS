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
    supplier_id = models.CharField(max_length=421, unique=True, null=True)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}'s contact person - {self.contact_person}"

class Category(models.Model):
    category_id = models.CharField(max_length=421, unique=True, null=True)
    category_name = models.CharField(max_length=25, default='General')    


    def __str__(self):
        return self.category_name 

class Item(models.Model):
    item_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    warrenty = models.DateField(null=True,blank=True,help_text="Warrenty Expire Date, if available")
    default_unit_of_measure = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True, null=True)
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
    unit_price = models.FloatField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    purchase_date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Calculate total cost
        self.unit_price = self.item.unit_price
        self.total_cost = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # Update stock automatically
        self.item.current_stock += self.quantity
        self.item.save()

    def __str__(self):
        return f"Purchase {self.purchase_no} - {self.item.name} -- {Item.objects.all()}"
   
class Project(models.Model):
    project_id = models.CharField(max_length=421, unique=True, null=True)
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

    items = models.ManyToManyField('Item', related_name='issue_items', blank=True)

    def __str__(self):
        return f"Issue {self.utilize_no} - {self.issued_to.first_name}"
    
