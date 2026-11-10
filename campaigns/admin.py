from django.contrib import admin
from .models import Campaign, Contact, ContactGroup, EmailLog, EmailTemplate, Workflow
# Register your models here.
admin.site.register(Contact)
admin.site.register(ContactGroup)
admin.site.register(EmailTemplate)
admin.site.register(Campaign)
admin.site.register(EmailLog)
admin.site.register(Workflow)
