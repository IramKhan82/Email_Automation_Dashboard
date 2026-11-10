from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

class ContactGroup(models.Model):
    name = models.CharField(max_length=100)
    contacts = models.ManyToManyField(Contact, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    name = models.CharField(max_length=150)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    recipients = models.ManyToManyField(Contact, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(ContactGroup, blank=True, related_name='campaigns')
    
    def __str__(self):
        return self.name

class EmailLog(models.Model):
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE,related_name='email_logs',null=True,blank=True)
    recipient_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    sent_at = models.DateTimeField(default=timezone.now)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Email to {self.recipient_email} for campaign {self.campaign.name} - {self.status}"

class Workflow(models.Model):

    TRIGGER_CHOICES = [
        ("new_contact", "When a New Contact is Added"),
    ]

    name = models.CharField(max_length=150)

    trigger = models.CharField(
        max_length=50,
        choices=TRIGGER_CHOICES
    )

    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name