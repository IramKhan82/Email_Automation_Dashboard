# Email Automation Dashboard

## 1. Project Overview

Email Automation Dashboard is a web-based application developed using Python and Django. It provides a centralized platform to create, manage, schedule, and automate email campaigns.

The application helps users manage contacts, organize contact groups, create reusable email templates, configure automation workflows, and track email delivery status.

## 2. Key Features

- **User Authentication:** Secure login and logout functionality.
- **Dashboard:** View campaign statistics and email activity.
- **Campaign Management:** Create, edit, delete, and send email campaigns.
- **Bulk Email Sending:** Send emails to multiple recipients and contact groups.
- **Email Scheduling:** Schedule campaigns for specific dates and times.
- **Contact Management:** Add, edit, and delete contacts.
- **CSV Import:** Import multiple contacts using CSV files.
- **Contact Groups:** Organize contacts into different groups.
- **Email Templates:** Create, edit, and reuse email templates.
- **Automation Workflows:** Create and manage email automation workflows.
- **Email Logs:** Track successful and failed email deliveries.
- **Campaign Tracking:** Monitor campaign statuses.

## 3. Technologies Used

- Python
- Django
- HTML5
- CSS3
- JavaScript
- SQLite
- Gmail SMTP

## 4. Project Setup

### Prerequisites

- Python installed on your system.
- pip package manager.

### Step 1: Extract the Project

Extract the project ZIP file and open the project directory in VS Code or a terminal.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the instructions to create your administrator username and password.

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

Log in using your account credentials.

## 5. Scheduled Email Automation

The application includes a Django management command to process scheduled email campaigns.

Run the following command:

```bash
python manage.py send_scheduled_campaigns
```

For automatic execution, Windows Task Scheduler can be configured to run this command periodically.

The computer must remain switched on and the scheduled task must be enabled for automatic execution.

## 6. Email Configuration

The application uses Gmail SMTP for email delivery.

Configure the required SMTP settings