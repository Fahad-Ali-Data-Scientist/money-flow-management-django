from django import forms
from .models import Company, Area, Customer, Payment, Employee, Expense, Bank, BankTransaction, Receivable, TransactionResponsibility

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_code', 'company_name', 'opening_balance']
        widgets = {
            'company_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company code'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter opening balance'}),
        }
        labels = {
            'company_code': 'Company Code',
            'company_name': 'Company Name',
            'opening_balance': 'Opening Balance',
        }
    
    def clean_company_code(self):
        company_code = self.cleaned_data.get('company_code')
        if Company.objects.filter(company_code=company_code).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("This company code is already in use.")
        return company_code 

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['area_code', 'name', 'description']
        widgets = {
            'area_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter area code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter area name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter area description', 'rows': 3}),
        }
        labels = {
            'area_code': 'Area Code',
            'name': 'Area Name',
            'description': 'Description',
        }
    
    def clean_area_code(self):
        area_code = self.cleaned_data.get('area_code')
        if Area.objects.filter(area_code=area_code).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("This area code is already in use.")
        return area_code
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Area.objects.filter(name=name).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("This area name is already in use.")
        return name

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_code', 'name_english', 'name_urdu', 'shop_name', 
            'phone_number', 'opening_balance', 'credit_limit_amount', 
            'credit_limit_days', 'address', 'area', 'category'
        ]
        widgets = {
            'customer_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer code'}),
            'name_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name in English'}),
            'name_urdu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name in Urdu'}),
            'shop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter shop name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter opening balance'}),
            'credit_limit_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter credit limit amount'}),
            'credit_limit_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter credit limit days'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'customer_code': 'Customer Code',
            'name_english': 'Name (English)',
            'name_urdu': 'Name (Urdu)',
            'shop_name': 'Shop Name',
            'phone_number': 'Phone Number',
            'opening_balance': 'Opening Balance',
            'credit_limit_amount': 'Credit Limit Amount',
            'credit_limit_days': 'Credit Limit Days',
            'address': 'Address',
            'area': 'Area',
            'category': 'Customer Category',
        }
    
    def clean_customer_code(self):
        customer_code = self.cleaned_data.get('customer_code')
        if Customer.objects.filter(customer_code=customer_code).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("This customer code is already in use.")
        return customer_code

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['customer', 'amount', 'payment_date', 'due_date', 'notes', 'is_paid']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter notes', 'rows': 3}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'customer': 'Customer',
            'amount': 'Amount',
            'payment_date': 'Payment Date',
            'due_date': 'Due Date',
            'notes': 'Notes',
            'is_paid': 'Is Paid',
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_code', 'name', 'category', 'phone_number', 
            'referred_by', 'email', 'cnic', 'date_of_birth', 
            'date_of_joining', 'date_of_resignation', 'address', 'status'
        ]
        widgets = {
            'employee_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter employee code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter employee name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'referred_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter referrer name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CNIC number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_resignation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'employee_code': 'Employee Code',
            'name': 'Employee Name',
            'category': 'Employee Category (Role)',
            'phone_number': 'Phone Number',
            'referred_by': 'Referred By',
            'email': 'Email Address',
            'cnic': 'CNIC Number',
            'date_of_birth': 'Date of Birth',
            'date_of_joining': 'Date of Joining',
            'date_of_resignation': 'Date of Resignation',
            'address': 'Address',
            'status': 'Status',
        }
    
    def clean_employee_code(self):
        employee_code = self.cleaned_data.get('employee_code')
        if Employee.objects.filter(employee_code=employee_code).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("This employee code is already in use.")
        return employee_code

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_code', 'name', 'amount', 'category', 'date', 'description']
        widgets = {
            'expense_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense Code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense Name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
        }
        labels = {
            'expense_code': 'Expense Code',
            'name': 'Expense Name',
            'amount': 'Amount',
            'category': 'Category',
            'date': 'Date',
            'description': 'Description',
        }

    def clean_expense_code(self):
        expense_code = self.cleaned_data.get('expense_code')
        if self.instance.pk:
            # If this is an existing expense, exclude this instance from the unique check
            if Expense.objects.filter(expense_code=expense_code).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This expense code is already in use.')
        else:
            # If this is a new expense
            if Expense.objects.filter(expense_code=expense_code).exists():
                raise forms.ValidationError('This expense code is already in use.')
        return expense_code

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['bank_code', 'name', 'account_number', 'branch', 'opening_balance']
        widgets = {
            'bank_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opening Balance'}),
        }
        labels = {
            'bank_code': 'Bank Code',
            'name': 'Bank Name',
            'account_number': 'Account Number',
            'branch': 'Branch',
            'opening_balance': 'Opening Balance',
        }

    def clean_bank_code(self):
        bank_code = self.cleaned_data.get('bank_code')
        if self.instance.pk:
            # If this is an existing bank, exclude this instance from the unique check
            if Bank.objects.filter(bank_code=bank_code).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This bank code is already in use.')
        else:
            # If this is a new bank
            if Bank.objects.filter(bank_code=bank_code).exists():
                raise forms.ValidationError('This bank code is already in use.')
        return bank_code

class BankTransactionForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ['bank', 'transaction_type', 'amount', 'date', 'description']
        widgets = {
            'bank': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3}),
        }
        labels = {
            'bank': 'Bank',
            'transaction_type': 'Transaction Type',
            'amount': 'Amount',
            'date': 'Date',
            'description': 'Description',
        }

class ReceivableForm(forms.ModelForm):
    class Meta:
        model = Receivable
        fields = ['person_code', 'person_name', 'due_date', 'amount']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'person_code': forms.TextInput(attrs={'class': 'form-control'}),
            'person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class TransactionResponsibilityForm(forms.ModelForm):
    class Meta:
        model = TransactionResponsibility
        fields = ['transaction_id', 'amount', 'transaction_date', 'transaction_type', 
                  'description', 'source_entity_type', 'source_entity_id', 
                  'destination_entity_type', 'destination_entity_id', 'responsible_person']
        widgets = {
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transaction_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'source_entity_type': forms.Select(attrs={'class': 'form-control'}),
            'source_entity_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_entity_type': forms.Select(attrs={'class': 'form-control'}),
            'destination_entity_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'responsible_person': forms.Select(attrs={'class': 'form-control'}),
        } 