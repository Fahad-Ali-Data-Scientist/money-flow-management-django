from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q, Avg, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.urls import reverse
import csv
import json
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.conf import settings
import os
import tempfile
from decimal import Decimal


from .models import (
    Company, Area, Customer, Payment, Employee, Expense, Bank, BankTransaction,
    Receivable, TransactionResponsibility
)
from .forms import (
    CompanyForm, AreaForm, CustomerForm, PaymentForm, EmployeeForm, ExpenseForm,
    BankForm, BankTransactionForm, ReceivableForm, TransactionResponsibilityForm
)

@login_required
def dashboard(request):
    # Get time period from request
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    # Calculate date range based on selected period
    if period == 'day':
        start_date = today
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # month (default)
        start_date = today.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    
    # Data for summary cards
    payments = Payment.objects.filter(payment_date__range=[start_date, end_date])
    # payments = Payment.objects.filter(date__range=[start_date, end_date])
    expenses = Expense.objects.filter(date__range=[start_date, end_date])
    
    total_income = payments.aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
    total_expenses = expenses.aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
    net_income = total_income - total_expenses
    
    # Receivables information
    receivables = Receivable.objects.filter(is_paid=False)
    total_receivables = receivables.aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
    overdue_receivables = receivables.filter(due_date__lt=today)
    overdue_receivables_count = overdue_receivables.count()
    
    # System statistics
    total_companies = Company.objects.count()
    total_customers = Customer.objects.count()
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='active').count()
    total_banks = Bank.objects.count()
    
    # Count customers exceeding credit limit
    credit_exceeded_count = Customer.objects.filter(
        credit_limit_amount__gt=0,
        balance__gt=F('credit_limit_amount')
    ).count()
    
    # Employee category stats
    employee_category_stats = dict(Employee.objects.values_list('category').annotate(count=Count('id')).values_list('category', 'count'))
    
    # Area data
    area_data = Area.objects.annotate(
        customer_count=Count('customer'),
        total_balance=Coalesce(Sum('customer__balance'), Decimal('0.00'))
    ).values('name', 'customer_count', 'total_balance')
    
    # Chart data for daily collections
    daily_collections = []
    
    # Prepare date range for chart
    current_date = start_date
    chart_labels = []
    chart_data = []
    
    while current_date <= end_date:
        daily_amount = Payment.objects.filter(payment_date=current_date).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0.00'))
        )['total']
        
        chart_labels.append(current_date.strftime('%d %b'))
        chart_data.append(float(daily_amount))
        
        current_date += timedelta(days=1)
    
    # Expense category breakdown
    expense_categories = expenses.values('category').annotate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    ).order_by('-total')
    
    expense_category_labels = [item['category'] for item in expense_categories]
    expense_category_data = [float(item['total']) for item in expense_categories]
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'total_receivables': total_receivables,
        'overdue_receivables_count': overdue_receivables_count,
        'total_companies': total_companies,
        'total_customers': total_customers,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_banks': total_banks,
        'credit_exceeded_count': credit_exceeded_count,
        'employee_category_stats': employee_category_stats,
        'area_data': area_data,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'expense_category_labels': json.dumps(expense_category_labels),
        'expense_category_data': json.dumps(expense_category_data),
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def companies(request):
    companies = Company.objects.all()
    form = CompanyForm()
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company added successfully!')
            return redirect('companies')
    
    context = {
        'companies': companies,
        'form': form,
        'active_page': 'companies'
    }
    return render(request, 'dashboard/companies.html', context)

@login_required
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated successfully!')
            return redirect('companies')
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'active_page': 'companies'
    }
    return render(request, 'dashboard/edit_company.html', context)

@login_required
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        company.delete()
        messages.success(request, 'Company deleted successfully!')
        return redirect('companies')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def areas(request):
    areas = Area.objects.all()
    form = AreaForm()
    
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Area added successfully!')
            return redirect('areas')
    
    context = {
        'areas': areas,
        'form': form,
        'active_page': 'areas'
    }
    return render(request, 'dashboard/areas.html', context)

@login_required
def edit_area(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    
    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Area updated successfully!')
            return redirect('areas')
    else:
        form = AreaForm(instance=area)
    
    context = {
        'form': form,
        'area': area,
        'active_page': 'areas'
    }
    return render(request, 'dashboard/edit_area.html', context)

@login_required
def delete_area(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    
    if request.method == 'POST':
        try:
            # Check if the area has customers
            customer_count = area.customer_set.count()
            if customer_count > 0:
                # Update customers to have no area
                area.customer_set.update(area=None)
            
            # Delete the area
            area.delete()
            messages.success(request, 'Area deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting area: {str(e)}')
        return redirect('areas')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def customers(request):
    customers = Customer.objects.all()
    form = CustomerForm()
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('customers')
    
    context = {
        'customers': customers,
        'form': form,
        'active_page': 'customers'
    }
    return render(request, 'dashboard/customers.html', context)

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    payments = Payment.objects.filter(customer=customer).order_by('-payment_date')
    payment_form = PaymentForm(initial={'customer': customer})
    
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            
            # Update customer balance
            if payment.is_paid:
                customer.balance -= payment.amount
                customer.save()
            
            payment.save()
            messages.success(request, 'Payment recorded successfully!')
            return redirect('customer_detail', customer_id=customer.id)
    
    context = {
        'customer': customer,
        'payments': payments,
        'payment_form': payment_form,
        'active_page': 'customers'
    }
    return render(request, 'dashboard/customer_detail.html', context)

@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'active_page': 'customers'
    }
    return render(request, 'dashboard/edit_customer.html', context)

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customers')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def payments(request):
    payments = Payment.objects.all().order_by('-payment_date')
    form = PaymentForm()
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Update customer balance if payment is marked as paid
            if payment.is_paid:
                customer = payment.customer
                customer.balance -= payment.amount
                customer.save()
            
            payment.save()
            messages.success(request, 'Payment added successfully!')
            return redirect('payments')
    
    context = {
        'payments': payments,
        'form': form,
        'active_page': 'payments'
    }
    return render(request, 'dashboard/payments.html', context)

@login_required
def edit_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    old_payment_status = payment.is_paid
    old_amount = payment.amount
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            updated_payment = form.save(commit=False)
            
            # Handle payment status change and its effect on customer balance
            customer = updated_payment.customer
            
            # Reverse old effect on balance
            if old_payment_status:
                customer.balance += old_amount
            
            # Apply new effect on balance
            if updated_payment.is_paid:
                customer.balance -= updated_payment.amount
            
            customer.save()
            updated_payment.save()
            
            messages.success(request, 'Payment updated successfully!')
            return redirect('payments')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'active_page': 'payments'
    }
    return render(request, 'dashboard/edit_payment.html', context)

@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        # Adjust customer balance if payment was marked as paid
        if payment.is_paid:
            customer = payment.customer
            customer.balance += payment.amount
            customer.save()
        
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('payments')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def employees(request):
    employees = Employee.objects.all()
    form = EmployeeForm()
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employees')
    
    context = {
        'employees': employees,
        'form': form,
        'active_page': 'employees'
    }
    return render(request, 'dashboard/employees.html', context)

@login_required
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employees')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
        'active_page': 'employees'
    }
    return render(request, 'dashboard/edit_employee.html', context)

@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        try:
            # Delete the employee
            employee.delete()
            messages.success(request, 'Employee deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
        return redirect('employees')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def expenses(request):
    expenses = Expense.objects.all().order_by('-date')
    form = ExpenseForm()
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expenses')
    
    # Get expense statistics for dashboard
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    expense_by_category = {}
    for category in dict(Expense.CATEGORY_CHOICES).keys():
        category_total = expenses.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        if category_total > 0:
            expense_by_category[dict(Expense.CATEGORY_CHOICES)[category]] = category_total
    
    context = {
        'expenses': expenses,
        'form': form,
        'active_page': 'expenses',
        'total_expenses': total_expenses,
        'expense_by_category': expense_by_category
    }
    return render(request, 'dashboard/expenses.html', context)

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses')
    else:
        form = ExpenseForm(instance=expense)
    
    context = {
        'form': form,
        'expense': expense,
        'active_page': 'expenses'
    }
    return render(request, 'dashboard/edit_expense.html', context)

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        try:
            expense.delete()
            messages.success(request, 'Expense deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting expense: {str(e)}')
        return redirect('expenses')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def expense_report(request):
    # Default date range (this month)
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today
    
    # Get filter parameters
    if request.method == 'GET' and 'start_date' in request.GET and 'end_date' in request.GET:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    category_filter = request.GET.get('category', '')
    
    # Filter expenses
    expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date)
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    
    # Aggregate data for charts
    category_data = {}
    for expense in expenses:
        category_name = expense.get_category_display()
        if category_name in category_data:
            category_data[category_name] += expense.amount
        else:
            category_data[category_name] = expense.amount
    
    # Date-based expense data
    date_data = {}
    for expense in expenses:
        date_str = expense.date.strftime('%Y-%m-%d')
        if date_str in date_data:
            date_data[date_str] += expense.amount
        else:
            date_data[date_str] = expense.amount
    
    context = {
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
        'category_filter': category_filter,
        'category_choices': Expense.CATEGORY_CHOICES,
        'total_amount': expenses.aggregate(Sum('amount'))['amount__sum'] or 0,
        'category_data': category_data,
        'date_data': date_data,
        'active_page': 'expenses'
    }
    return render(request, 'dashboard/expense_report.html', context)

@login_required
def banks(request):
    banks = Bank.objects.all()
    form = BankForm()
    
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank added successfully!')
            return redirect('banks')
    
    context = {
        'banks': banks,
        'form': form,
        'active_page': 'banks',
        'total_balance': banks.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    }
    return render(request, 'dashboard/banks.html', context)

@login_required
def edit_bank(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    old_opening_balance = bank.opening_balance
    
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            new_bank = form.save(commit=False)
            # Adjust current balance based on change in opening balance
            balance_difference = new_bank.opening_balance - old_opening_balance
            new_bank.current_balance += balance_difference
            new_bank.save()
            
            messages.success(request, 'Bank updated successfully!')
            return redirect('banks')
    else:
        form = BankForm(instance=bank)
    
    context = {
        'form': form,
        'bank': bank,
        'active_page': 'banks'
    }
    return render(request, 'dashboard/edit_bank.html', context)

@login_required
def delete_bank(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    
    if request.method == 'POST':
        try:
            # Check if the bank has transactions
            if bank.banktransaction_set.exists():
                messages.error(request, 'Cannot delete bank as it has transactions. Remove the transactions first.')
                return redirect('banks')
            
            bank.delete()
            messages.success(request, 'Bank deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting bank: {str(e)}')
        return redirect('banks')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def bank_transactions(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    transactions = bank.banktransaction_set.all().order_by('-date')
    
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = float(request.POST.get('amount', 0))
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        
        if transaction_type and amount > 0 and date:
            transaction = BankTransaction.objects.create(
                bank=bank,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                date=datetime.strptime(date, '%Y-%m-%d').date()
            )
            
            # Update bank balance
            if transaction_type in ['deposit', 'interest']:
                bank.current_balance += amount
            elif transaction_type in ['withdrawal', 'fee']:
                bank.current_balance -= amount
            
            bank.save()
            messages.success(request, 'Transaction recorded successfully!')
            return redirect('bank_transactions', bank_id=bank.id)
        else:
            messages.error(request, 'Please provide all required fields for the transaction.')
    
    context = {
        'bank': bank,
        'transactions': transactions,
        'transaction_types': BankTransaction.TRANSACTION_TYPE_CHOICES,
        'active_page': 'banks'
    }
    return render(request, 'dashboard/bank_transactions.html', context)

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(BankTransaction, id=transaction_id)
    bank = transaction.bank
    
    if request.method == 'POST':
        try:
            # Reverse the effect on bank balance
            if transaction.transaction_type in ['deposit', 'interest']:
                bank.current_balance -= transaction.amount
            elif transaction.transaction_type in ['withdrawal', 'fee']:
                bank.current_balance += transaction.amount
            
            bank.save()
            transaction.delete()
            
            messages.success(request, 'Transaction deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting transaction: {str(e)}')
        return redirect('bank_transactions', bank_id=bank.id)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def receivables(request):
    receivables_list = Receivable.objects.all()
    form = ReceivableForm()
    
    if request.method == 'POST':
        form = ReceivableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receivable added successfully!')
            return redirect('receivables')
    
    # Calculate total outstanding amount
    total_outstanding = sum(r.outstanding_amount for r in receivables_list)
    
    # Get overdue receivables
    overdue_receivables = [r for r in receivables_list if r.is_overdue]
    total_overdue = sum(r.outstanding_amount for r in overdue_receivables)
    
    context = {
        'receivables': receivables_list,
        'form': form,
        'active_page': 'receivables',
        'total_outstanding': total_outstanding,
        'total_overdue': total_overdue,
        'overdue_count': len(overdue_receivables)
    }
    return render(request, 'dashboard/receivables.html', context)

@login_required
def edit_receivable(request, receivable_id):
    receivable = get_object_or_404(Receivable, id=receivable_id)
    
    if request.method == 'POST':
        form = ReceivableForm(request.POST, instance=receivable)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receivable updated successfully!')
            return redirect('receivables')
    else:
        form = ReceivableForm(instance=receivable)
    
    context = {
        'form': form,
        'receivable': receivable,
        'active_page': 'receivables'
    }
    return render(request, 'dashboard/edit_receivable.html', context)

@login_required
def delete_receivable(request, receivable_id):
    receivable = get_object_or_404(Receivable, id=receivable_id)
    
    if request.method == 'POST':
        receivable.delete()
        messages.success(request, 'Receivable deleted successfully!')
        return redirect('receivables')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def mark_receivable_paid(request, receivable_id):
    receivable = get_object_or_404(Receivable, id=receivable_id)
    
    if request.method == 'POST':
        receivable.is_paid = True
        receivable.save()
        messages.success(request, 'Receivable marked as paid!')
        return redirect('receivables')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def money_flow(request):
    # Get transactions for the last 30 days by default
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.method == 'GET':
        if 'start_date' in request.GET and 'end_date' in request.GET:
            try:
                start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
    
    # Get all transaction responsibilities in the date range
    transactions = TransactionResponsibility.objects.filter(
        transaction_date__range=[start_date, end_date]
    ).order_by('-transaction_date')
    
    # Prepare data for visualization
    entity_types = dict(TransactionResponsibility.ENTITY_TYPE_CHOICES)
    transaction_types = dict(TransactionResponsibility.TRANSACTION_TYPE_CHOICES)
    
    # Money flow by entity type
    flow_by_entity = {}
    for entity_type in entity_types:
        incoming = transactions.filter(destination_entity_type=entity_type).aggregate(Sum('amount'))['amount__sum'] or 0
        outgoing = transactions.filter(source_entity_type=entity_type).aggregate(Sum('amount'))['amount__sum'] or 0
        flow_by_entity[entity_type] = {
            'name': entity_types[entity_type],
            'incoming': incoming,
            'outgoing': outgoing,
            'net': incoming - outgoing
        }
    
    # Money flow by transaction type
    flow_by_type = {}
    for t_type in transaction_types:
        total = transactions.filter(transaction_type=t_type).aggregate(Sum('amount'))['amount__sum'] or 0
        flow_by_type[t_type] = {
            'name': transaction_types[t_type],
            'total': total
        }
    
    # Money collected by employee
    employee_collection = {}
    for employee in Employee.objects.filter(status='active'):
        collected = transactions.filter(responsible_person=employee).aggregate(Sum('amount'))['amount__sum'] or 0
        if collected > 0:  # Only include employees who collected money
            employee_collection[employee.id] = {
                'name': employee.name,
                'collected': collected
            }
    
    # Form to add new transaction
    form = TransactionResponsibilityForm()
    if request.method == 'POST':
        form = TransactionResponsibilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction recorded successfully!')
            return redirect('money_flow')
    
    context = {
        'transactions': transactions,
        'flow_by_entity': flow_by_entity,
        'flow_by_type': flow_by_type,
        'employee_collection': employee_collection,
        'form': form,
        'active_page': 'money_flow',
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'dashboard/money_flow.html', context)

@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(TransactionResponsibility, id=transaction_id)
    
    if request.method == 'POST':
        form = TransactionResponsibilityForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('money_flow')
    else:
        form = TransactionResponsibilityForm(instance=transaction)
    
    context = {
        'form': form,
        'transaction': transaction,
        'active_page': 'money_flow'
    }
    return render(request, 'dashboard/edit_transaction.html', context)

@login_required
def delete_transaction_responsibility(request, transaction_id):
    transaction = get_object_or_404(TransactionResponsibility, id=transaction_id)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('money_flow')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def reports(request):
    # Get report parameters from request
    report_type = request.GET.get('report_type', 'date_collections')
    
    # Parse dates or set defaults
    try:
        start_date = datetime.strptime(request.GET.get('start_date', ''), '%Y-%m-%d').date()
    except ValueError:
        start_date = (timezone.now().date().replace(day=1))
        
    try:
        end_date = datetime.strptime(request.GET.get('end_date', ''), '%Y-%m-%d').date()
    except ValueError:
        # Last day of current month
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    
    # Get filter values
    selected_area = request.GET.get('area', '')
    selected_employee = request.GET.get('employee', '')
    selected_company = request.GET.get('company', '')
    
    # Prepare filter data for template
    areas = Area.objects.all()
    employees = Employee.objects.all()
    companies = Company.objects.all()
    
    # Initialize variables
    report_data = []
    report_summary = {}
    
    # Generate report based on type
    if report_type == 'date_collections':
        # Date-wise collections report
        query = Payment.objects.filter(date__range=[start_date, end_date])
        
        # Apply filters if provided
        if selected_area:
            query = query.filter(customer__area_id=selected_area)
        if selected_company:
            query = query.filter(customer__company_id=selected_company)
            
        # Get unique dates and prepare report data
        dates = query.dates('date', 'day')
        
        for current_date in dates:
            daily_payments = query.filter(date=current_date)
            total_amount = daily_payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
            payment_count = daily_payments.count()
            
            report_data.append({
                'date': current_date,
                'total_amount': total_amount,
                'payment_count': payment_count,
                'average_amount': total_amount / payment_count if payment_count > 0 else 0
            })
        
        # Sort by date
        report_data = sorted(report_data, key=lambda x: x['date'])
        
        # Calculate summary
        total_amount = sum(item['total_amount'] for item in report_data)
        total_count = sum(item['payment_count'] for item in report_data)
        
        report_summary = {
            'total_amount': total_amount,
            'total_count': total_count,
            'overall_average': total_amount / total_count if total_count > 0 else 0
        }
        
    elif report_type == 'employee_collections':
        # Employee-wise collections report
        query = Payment.objects.filter(date__range=[start_date, end_date])
        
        # Apply employee filter if provided
        if selected_employee:
            query = query.filter(employee_id=selected_employee)
            
        # Group by employee
        employee_data = query.values('employee__name').annotate(
            total_amount=Coalesce(Sum('amount'), 0),
            payment_count=Count('id')
        ).order_by('-total_amount')
        
        for item in employee_data:
            report_data.append({
                'employee_name': item['employee__name'],
                'total_amount': item['total_amount'],
                'payment_count': item['payment_count'],
                'average_amount': item['total_amount'] / item['payment_count'] if item['payment_count'] > 0 else 0
            })
        
        # Calculate summary
        total_amount = sum(item['total_amount'] for item in report_data)
        total_count = sum(item['payment_count'] for item in report_data)
        
        report_summary = {
            'total_amount': total_amount,
            'total_count': total_count,
            'overall_average': total_amount / total_count if total_count > 0 else 0
        }
        
    elif report_type == 'company_balance':
        # Company balances report
        query = Customer.objects.all()
        
        # Apply company filter if provided
        if selected_company:
            query = query.filter(company_id=selected_company)
            
        # Group by company
        company_data = query.values('company__name').annotate(
            customer_count=Count('id'),
            total_balance=Coalesce(Sum('balance'), 0)
        ).order_by('-total_balance')
        
        for item in company_data:
            report_data.append({
                'company_name': item['company__name'],
                'customer_count': item['customer_count'],
                'total_balance': item['total_balance'],
                'average_balance': item['total_balance'] / item['customer_count'] if item['customer_count'] > 0 else 0
            })
        
        # Calculate summary
        total_customers = sum(item['customer_count'] for item in report_data)
        total_balance = sum(item['total_balance'] for item in report_data)
        
        report_summary = {
            'total_customers': total_customers,
            'total_balance': total_balance,
            'overall_average': total_balance / total_customers if total_customers > 0 else 0
        }
        
    elif report_type == 'area_balance':
        # Area balances report
        query = Customer.objects.all()
        
        # Apply area filter if provided
        if selected_area:
            query = query.filter(area_id=selected_area)
            
        # Group by area
        area_data = query.values('area__name').annotate(
            customer_count=Count('id'),
            total_balance=Coalesce(Sum('balance'), 0)
        ).order_by('-total_balance')
        
        for item in area_data:
            report_data.append({
                'area_name': item['area__name'],
                'customer_count': item['customer_count'],
                'total_balance': item['total_balance'],
                'average_balance': item['total_balance'] / item['customer_count'] if item['customer_count'] > 0 else 0
            })
        
        # Calculate summary
        total_customers = sum(item['customer_count'] for item in report_data)
        total_balance = sum(item['total_balance'] for item in report_data)
        
        report_summary = {
            'total_customers': total_customers,
            'total_balance': total_balance,
            'overall_average': total_balance / total_customers if total_customers > 0 else 0
        }
        
    elif report_type == 'cash_receiver':
        # Cash receiver summary report
        query = TransactionResponsibility.objects.filter(transaction_date__range=[start_date, end_date])
        
        # Apply employee filter if provided
        if selected_employee:
            query = query.filter(responsible_person_id=selected_employee)
            
        # Group by employee and category
        employee_data = query.values('responsible_person__name', 'transaction_type').annotate(
            total_amount=Coalesce(Sum('amount'), 0),
            transaction_count=Count('id')
        ).order_by('-total_amount')
        
        for item in employee_data:
            report_data.append({
                'employee_name': item['responsible_person__name'],
                'category': item['transaction_type'],
                'total_amount': item['total_amount'],
                'transaction_count': item['transaction_count'],
                'average_amount': item['total_amount'] / item['transaction_count'] if item['transaction_count'] > 0 else 0
            })
        
        # Calculate summary
        total_amount = sum(item['total_amount'] for item in report_data)
        total_count = sum(item['transaction_count'] for item in report_data)
        
        report_summary = {
            'total_amount': total_amount,
            'total_count': total_count,
            'overall_average': total_amount / total_count if total_count > 0 else 0
        }
    
    context = {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'selected_area': selected_area,
        'selected_employee': selected_employee,
        'selected_company': selected_company,
        'areas': areas,
        'employees': employees,
        'companies': companies,
        'report_data': report_data,
        'report_summary': report_summary,
    }
    
    return render(request, 'dashboard/reports.html', context)

@login_required
def export_report(request, format_type):
    # Get report parameters from request
    report_type = request.GET.get('report_type', 'date_collections')
    
    # Parse dates or set defaults
    try:
        start_date = datetime.strptime(request.GET.get('start_date', ''), '%Y-%m-%d').date()
    except ValueError:
        start_date = (timezone.now().date().replace(day=1))
        
    try:
        end_date = datetime.strptime(request.GET.get('end_date', ''), '%Y-%m-%d').date()
    except ValueError:
        # Last day of current month
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    
    # Get filter values
    selected_area = request.GET.get('area', '')
    selected_employee = request.GET.get('employee', '')
    selected_company = request.GET.get('company', '')
    
    # Call the reports function to get the data
    context = reports(request).context
    report_data = context.get('report_data', [])
    report_summary = context.get('report_summary', {})
    
    # Handle export based on format type
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{start_date}_to_{end_date}.csv"'
        
        writer = csv.writer(response)
        
        # Write headers based on report type
        if report_type == 'date_collections':
            writer.writerow(['Date', 'Total Collections', 'Number of Payments', 'Average Amount'])
            # Write data rows
            for item in report_data:
                writer.writerow([
                    item['date'].strftime('%Y-%m-%d'),
                    item['total_amount'],
                    item['payment_count'],
                    item['average_amount']
                ])
            # Write summary
            writer.writerow(['Total', report_summary.get('total_amount', 0), report_summary.get('total_count', 0), report_summary.get('overall_average', 0)])
            
        elif report_type == 'employee_collections':
            writer.writerow(['Employee', 'Total Collections', 'Number of Payments', 'Average Amount'])
            # Write data rows
            for item in report_data:
                writer.writerow([
                    item['employee_name'],
                    item['total_amount'],
                    item['payment_count'],
                    item['average_amount']
                ])
            # Write summary
            writer.writerow(['Total', report_summary.get('total_amount', 0), report_summary.get('total_count', 0), report_summary.get('overall_average', 0)])
            
        elif report_type == 'company_balance':
            writer.writerow(['Company', 'Total Customers', 'Total Balance', 'Average Balance per Customer'])
            # Write data rows
            for item in report_data:
                writer.writerow([
                    item['company_name'],
                    item['customer_count'],
                    item['total_balance'],
                    item['average_balance']
                ])
            # Write summary
            writer.writerow(['Total', report_summary.get('total_customers', 0), report_summary.get('total_balance', 0), report_summary.get('overall_average', 0)])
            
        elif report_type == 'area_balance':
            writer.writerow(['Area', 'Total Customers', 'Total Balance', 'Average Balance per Customer'])
            # Write data rows
            for item in report_data:
                writer.writerow([
                    item['area_name'],
                    item['customer_count'],
                    item['total_balance'],
                    item['average_balance']
                ])
            # Write summary
            writer.writerow(['Total', report_summary.get('total_customers', 0), report_summary.get('total_balance', 0), report_summary.get('overall_average', 0)])
            
        elif report_type == 'cash_receiver':
            writer.writerow(['Employee', 'Category', 'Total Collected', 'Number of Transactions', 'Average Transaction'])
            # Write data rows
            for item in report_data:
                writer.writerow([
                    item['employee_name'],
                    item['category'],
                    item['total_amount'],
                    item['transaction_count'],
                    item['average_amount']
                ])
            # Write summary
            writer.writerow(['Total', '', report_summary.get('total_amount', 0), report_summary.get('total_count', 0), report_summary.get('overall_average', 0)])
        
        return response
        
    elif format_type == 'pdf':
        # Render template with context data
        html_string = render_to_string('dashboard/report_pdf.html', context)
        html = HTML(string=html_string)
        
        # Generate PDF
        result = html.write_pdf()
        
        # Create response
        response = HttpResponse(result, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{start_date}_to_{end_date}.pdf"'
        
        return response
    
    # If invalid format type, redirect back to reports
    return redirect('reports')
