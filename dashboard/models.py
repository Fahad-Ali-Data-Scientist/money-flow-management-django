from django.db import models
from django.utils import timezone
from django.db.models import Sum

# Create your models here.

class Company(models.Model):
    company_code = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=100)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['company_name']

class Area(models.Model):
    area_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_balance(self):
        return self.customer_set.aggregate(Sum('balance'))['balance__sum'] or 0
    
    @property
    def customer_count(self):
        return self.customer_set.count()
    
    class Meta:
        ordering = ['name']

class Customer(models.Model):
    CATEGORY_CHOICES = (
        ('regular', 'Regular'),
        ('vip', 'VIP'),
    )
    
    customer_code = models.CharField(max_length=20, unique=True)
    name_english = models.CharField(max_length=100)
    name_urdu = models.CharField(max_length=100, blank=True, null=True)
    shop_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_limit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_limit_days = models.PositiveIntegerField(default=0)
    address = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='regular')
    date_added = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name_english} ({self.shop_name})"
    
    @property
    def outstanding_amount(self):
        return sum(payment.outstanding_amount for payment in self.payment_set.all())
    
    @property
    def exceeds_credit_limit(self):
        return self.balance > self.credit_limit_amount
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.balance = self.opening_balance
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['name_english']

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    @property
    def outstanding_amount(self):
        return 0 if self.is_paid else self.amount
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.customer.name_english}"

class Employee(models.Model):
    CATEGORY_CHOICES = (
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
        ('salesperson', 'Salesperson'),
        ('accountant', 'Accountant'),
        ('admin', 'Administrative Staff'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    )
    
    employee_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    phone_number = models.CharField(max_length=20)
    referred_by = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cnic = models.CharField(max_length=20, blank=True, null=True, verbose_name="CNIC")
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(default=timezone.now)
    date_of_resignation = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.name} ({self.employee_code})"
    
    def save(self, *args, **kwargs):
        if self.date_of_resignation and self.status == 'active':
            self.status = 'resigned'
        elif not self.date_of_resignation and self.status == 'resigned':
            self.date_of_resignation = None
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['name']

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('marketing', 'Marketing'),
        ('travel', 'Travel'),
        ('taxes', 'Taxes'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    expense_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.amount}"
        
    class Meta:
        ordering = ['-date']

class Bank(models.Model):
    bank_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    branch = models.CharField(max_length=100, blank=True, null=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.account_number}"
    
    def save(self, *args, **kwargs):
        # Set current balance to opening balance when creating a new bank
        if not self.pk:
            self.current_balance = self.opening_balance
        super().save(*args, **kwargs)

class BankTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('interest', 'Interest'),
        ('fee', 'Fee'),
        ('transfer', 'Transfer'),
    ]
    
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-created_at']

class Receivable(models.Model):
    person_code = models.CharField(max_length=20, unique=True)
    person_name = models.CharField(max_length=100)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.person_name} - {self.amount}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and not self.is_paid
    
    @property
    def outstanding_amount(self):
        return 0 if self.is_paid else self.amount
    
    class Meta:
        ordering = ['due_date']

class TransactionResponsibility(models.Model):
    ENTITY_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('bank', 'Bank'),
        ('company', 'Company'),
    )
    
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('expense', 'Expense'),
    )
    
    transaction_id = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Source entity (from where the money comes)
    source_entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    source_entity_id = models.IntegerField()
    
    # Destination entity (to where the money goes)
    destination_entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    destination_entity_id = models.IntegerField()
    
    # Person responsible for the transaction
    responsible_person = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='transactions_responsible')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type} - {self.amount}"
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name_plural = "Transaction Responsibilities"
