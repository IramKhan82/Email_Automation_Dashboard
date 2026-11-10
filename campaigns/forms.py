from django import forms
from .models import Campaign, Contact, ContactGroup, EmailTemplate, Workflow

# CAMPAIGN FORM
class CampaignForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects.all(),
        required=False,
        empty_label="Select an Email Template",
        label="Choose Email Template"
    )

    class Meta:
        model = Campaign
        fields = [
            "name",
            "subject",
            "body",
            "recipients",
            "groups",
            "scheduled_at"
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Campaign name"
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Email subject"
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Write your email..."
            }),
            "recipients": forms.CheckboxSelectMultiple(attrs={
                "class": "choice-list"
            }),
            "groups": forms.CheckboxSelectMultiple(attrs={
                "class": "choice-list"
            }),
            "scheduled_at": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local"
            }),
        }

# CONTACT FORM
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter contact name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email address"
            }),
        }

# CONTACT GROUP FORM
class ContactGroupForm(forms.ModelForm):
    class Meta:
        model = ContactGroup
        fields = ["name", "contacts"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter group name"
            }),
            "contacts": forms.CheckboxSelectMultiple(),
        }
# EMAIL TEMPLATE FORM
class EmailTemplateForm(forms.ModelForm):

    class Meta:
        model = EmailTemplate
        fields = ["name", "subject", "body"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Template name"
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Email subject"
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Write your email template..."
            }),
        }

# WORKFLOW FORM
class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = [
            "name",
            "trigger",
            "template",
            "is_active",
        ]