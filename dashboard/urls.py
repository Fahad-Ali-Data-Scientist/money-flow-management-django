from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Company URLs
    path('companies/', views.companies, name='companies'),
    path('companies/edit/<int:company_id>/', views.edit_company, name='edit_company'),
    path('companies/delete/<int:company_id>/', views.delete_company, name='delete_company'),
    
    # Area URLs
    path('areas/', views.areas, name='areas'),
    path('areas/edit/<int:area_id>/', views.edit_area, name='edit_area'),
    path('areas/delete/<int:area_id>/', views.delete_area, name='delete_area'),
    
    # Customer URLs
    path('customers/', views.customers, name='customers'),
    path('customers/detail/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/edit/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    
    # Payment URLs
    path('payments/', views.payments, name='payments'),
    path('payments/edit/<int:payment_id>/', views.edit_payment, name='edit_payment'),
    path('payments/delete/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    
    # Employee URLs
    path('employees/', views.employees, name='employees'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    # Expense URLs
    path('expenses/', views.expenses, name='expenses'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('expenses/report/', views.expense_report, name='expense_report'),
    
    # Bank URLs
    path('banks/', views.banks, name='banks'),
    path('banks/edit/<int:bank_id>/', views.edit_bank, name='edit_bank'),
    path('banks/delete/<int:bank_id>/', views.delete_bank, name='delete_bank'),
    path('banks/transactions/<int:bank_id>/', views.bank_transactions, name='bank_transactions'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    
    # Receivable URLs
    path('receivables/', views.receivables, name='receivables'),
    path('receivables/edit/<int:receivable_id>/', views.edit_receivable, name='edit_receivable'),
    path('receivables/delete/<int:receivable_id>/', views.delete_receivable, name='delete_receivable'),
    path('receivables/mark-paid/<int:receivable_id>/', views.mark_receivable_paid, name='mark_receivable_paid'),
    
    # Money Flow URLs
    path('money-flow/', views.money_flow, name='money_flow'),
    path('money-flow/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('money-flow/delete/<int:transaction_id>/', views.delete_transaction_responsibility, name='delete_transaction_responsibility'),
    
    # Reports URLs
    path('reports/', views.reports, name='reports'),
    path('reports/export/<str:format_type>/', views.export_report, name='export_report'),
] 