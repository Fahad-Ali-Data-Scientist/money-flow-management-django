# Money Flow Management – Django

A Django web app for small businesses to track **where money comes from and where it goes**: customers, payments, receivables, expenses, employees and bank accounts, with reports in one dashboard.

## Features

| Module | What you can do |
|---|---|
| Companies and areas | Organise customers by company and sales area |
| Customers | Customer list, detail page and balances |
| Payments and receivables | Record payments, track receivables and mark them paid |
| Expenses | Log expenses and see an expense report |
| Employees | Manage staff records |
| Banks | Bank accounts and their transaction history |
| Money flow | Track who is responsible for each transaction |
| Reports | Dashboard and summary reports |
| Auth | Login, logout, registration, user list and JWT API tokens (`/api/token/`) |

## Data model

`Company` → `Area` → `Customer` → `Payment` / `Receivable`
`Employee`, `Expense`, `Bank` → `BankTransaction`, `TransactionResponsibility`

## Setup

```bash
git clone https://github.com/Fahad-Ali-Data-Scientist/money-flow-management-django.git
cd money-flow-management-django
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tech stack

Python · Django · Django REST Framework · Simple JWT · SQLite · HTML / CSS
