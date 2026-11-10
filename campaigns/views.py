from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Campaign, Contact, ContactGroup, EmailLog, EmailTemplate, Workflow
from .services import send_campaign_emails
from .forms import CampaignForm, ContactForm, ContactGroupForm, EmailTemplateForm, WorkflowForm
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from datetime import timedelta
import csv

def dashboard(request):
    total_campaigns = Campaign.objects.count()

    total_contacts = Contact.objects.filter(
        is_active=True
    ).count()

    sent_emails = EmailLog.objects.filter(
        status="sent"
    ).count()

    failed_emails = EmailLog.objects.filter(
        status="failed"
    ).count()

    scheduled_campaigns = Campaign.objects.filter(
        status="scheduled"
    ).count()

    recent_campaigns = Campaign.objects.order_by(
        "-created_at"
    )[:5]

    # Workflow Analytics
    total_workflows = Workflow.objects.count()

    active_workflows = Workflow.objects.filter(
        is_active=True
    ).count()

    workflow_sent_emails = EmailLog.objects.filter(
        campaign__isnull=True,
        status="sent"
    ).count()

    campaign_sent_emails = EmailLog.objects.filter(
        campaign__isnull=False,
        status="sent"
    ).count()

        # Campaign Status Analytics
    draft_campaigns = Campaign.objects.filter(status="draft").count()
    sending_campaigns = Campaign.objects.filter(status="sending").count()
    sent_campaigns = Campaign.objects.filter(status="sent").count()
    failed_campaigns = Campaign.objects.filter(status="failed").count()

    context = {
        "draft_campaigns": draft_campaigns,
        "sending_campaigns": sending_campaigns,
        "sent_campaigns": sent_campaigns,
        "failed_campaigns": failed_campaigns,
        "total_campaigns": total_campaigns,
        "total_contacts": total_contacts,
        "sent_emails": sent_emails,
        "failed_emails": failed_emails,
        "scheduled_campaigns": scheduled_campaigns,
        "recent_campaigns": recent_campaigns,

        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "workflow_sent_emails": workflow_sent_emails,
        "campaign_sent_emails": campaign_sent_emails,
    }

    return render(request, "campaigns/dashboard.html", context)

def dashboard_live_data(request):

    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    # Live Statistics
    stats = {
        "total_campaigns": Campaign.objects.count(),

        "total_contacts": Contact.objects.filter(
            is_active=True
        ).count(),

        "sent_emails": EmailLog.objects.filter(
            status="sent"
        ).count(),

        "failed_emails": EmailLog.objects.filter(
            status="failed"
        ).count(),

        "scheduled_campaigns": Campaign.objects.filter(
            status="scheduled"
        ).count(),

        "active_workflows": Workflow.objects.filter(
            is_active=True
        ).count(),
    }

    # Last 7 Days Email Performance
    chart_labels = []
    sent_data = []
    failed_data = []

    for i in range(7):

        current_date = start_date + timedelta(days=i)

        chart_labels.append(current_date.strftime("%d %b"))

        daily_logs = EmailLog.objects.filter(
            sent_at__date=current_date
        )

        sent_data.append(
            daily_logs.filter(status="sent").count()
        )

        failed_data.append(
            daily_logs.filter(status="failed").count()
        )

    # Recent Email Activity
    recent_logs = EmailLog.objects.select_related(
        "campaign"
    ).order_by("-sent_at")[:6]

    activities = []

    for log in recent_logs:

        activities.append({
            "source": (
                log.campaign.name
                if log.campaign
                else "Workflow Email"
            ),
            "recipient": log.recipient_email,
            "status": log.status,
            "time": log.sent_at.strftime("%d %b, %I:%M %p"),
        })

    return JsonResponse({
        "stats": stats,

        "chart": {
            "labels": chart_labels,
            "sent": sent_data,
            "failed": failed_data,
        },

        "activities": activities,
    })

def campaign_list(request):
    campaigns = Campaign.objects.order_by("-created_at")

    for campaign in campaigns:
        campaign.sent_count = campaign.email_logs.filter(status="sent").count()
        campaign.failed_count = campaign.email_logs.filter(status="failed").count()

    return render(
        request,
        "campaigns/campaign_list.html",
        {"campaigns": campaigns}
    )


def campaign_create(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)

        if form.is_valid():
            campaign = form.save()

            if campaign.scheduled_at and campaign.scheduled_at > timezone.now():
                campaign.status = "scheduled"
            else:
                campaign.status = "draft"

            campaign.save()

            messages.success(request, "Campaign created successfully!")
            return redirect("campaign_list")

    else:
        form = CampaignForm()

    return render(request,"campaigns/campaign_form.html",{"form": form})

def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)

        if form.is_valid():
            campaign = form.save()

            if campaign.scheduled_at and campaign.scheduled_at > timezone.now():
                campaign.status = "scheduled"
            else:
                campaign.status = "draft"

            campaign.save()
            return redirect("campaign_list")

    else:
        form = CampaignForm(instance=campaign)

    return render(request,"campaigns/campaign_form.html",{"form": form, "edit_mode": True})


def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":
        campaign.delete()
        return redirect("campaign_list")

    return render(request,"campaigns/campaign_confirm_delete.html",{"campaign": campaign})

def campaign_send(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":

        sent_count, failed_count = send_campaign_emails(campaign)

        if sent_count == 0 and failed_count == 0:
            messages.error(
                request,
                "Please add active recipients or select a contact group."
            )
            return redirect("campaign_list")

        return render(
            request,
            "campaigns/campaign_success.html",
            {
                "campaign": campaign,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_count": sent_count + failed_count,
            }
        )

    return render(
        request,
        "campaigns/campaign_send_confirm.html",
        {"campaign": campaign}
    )

# CONTACT MANAGEMENT

def contact_list(request):
    contacts = Contact.objects.all().order_by("-created_at")

    return render(request, "campaigns/contact_list.html", {
        "contacts": contacts
    })


def import_contacts(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.lower().endswith(".csv"):
            messages.error(request, "Please upload a CSV file.")
            return redirect("contact_list")

        try:
            decoded_file = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.DictReader(decoded_file)

            imported_count = 0
            duplicate_count = 0
            invalid_count = 0

            for row in reader:
                name = (row.get("name") or "").strip()
                email = (row.get("email") or "").strip()

                if not name or not email:
                    invalid_count += 1
                    continue

                contact, created = Contact.objects.get_or_create(
                    email=email,
                    defaults={"name": name}
                )

                if created:
                    imported_count += 1
                else:
                    duplicate_count += 1

            if imported_count:
                messages.success(
                    request,
                    f"{imported_count} new contacts imported successfully!"
                )

            if duplicate_count:
                messages.warning(
                    request,
                    f"{duplicate_count} duplicate contacts skipped."
                )

            if invalid_count:
                messages.error(
                    request,
                    f"{invalid_count} rows skipped due to missing name or email."
                )

            if not imported_count and not duplicate_count and not invalid_count:
                messages.warning(request, "The CSV file is empty.")

        except Exception as e:
            messages.error(request, f"Error importing CSV: {e}")

    else:
        messages.error(request, "Please select a CSV file.")

    return redirect("contact_list")


def contact_create(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            contact = form.save()

            # Find active workflows for new contacts
            workflows = Workflow.objects.filter(
                trigger="new_contact",
                is_active=True
            )

            # Send automatic emails
            for workflow in workflows:
                try:
                    send_mail(
                        subject=workflow.template.subject,
                        message=workflow.template.body,
                        from_email=None,
                        recipient_list=[contact.email],
                        fail_silently=False,
                    )

                    EmailLog.objects.create(
                        campaign=None,
                        recipient_email=contact.email,
                        status="sent",
                    )

                except Exception as e:
                    EmailLog.objects.create(
                        campaign=None,
                        recipient_email=contact.email,
                        status="failed",
                        error_message=str(e)
                    )

                    print(f"Workflow email failed: {e}")

            messages.success(
                request,
                "Contact added successfully!"
            )

            return redirect("contact_list")

    else:
        form = ContactForm()

    return render(request, "campaigns/contact_form.html", {
        "form": form,
        "title": "Add Contact"
    })

def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)

        if form.is_valid():
            form.save()
            messages.success(request, "Contact updated successfully!")
            return redirect("contact_list")
    else:
        form = ContactForm(instance=contact)

    return render(request, "campaigns/contact_form.html", {
        "form": form,
        "title": "Edit Contact"
    })


def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contact deleted successfully!")
        return redirect("contact_list")

    return render(request, "campaigns/contact_confirm_delete.html", {
        "contact": contact
    })

def contact_bulk_delete(request):

    if request.method == "POST":

        selected_ids = request.POST.getlist("selected_contacts")

        if selected_ids:
            deleted_count, _ = Contact.objects.filter(
                pk__in=selected_ids
            ).delete()

            messages.success(
                request,
                f"{deleted_count} contacts deleted successfully!"
            )
        else:
            messages.warning(
                request,
                "Please select at least one contact."
            )

    return redirect("contact_list")

# CONTACT GROUP MANAGEMENT

def group_list(request):
    groups = ContactGroup.objects.all().order_by("-created_at")
    return render(request, "campaigns/group_list.html", {
        "groups": groups
    })


def group_create(request):
    if request.method == "POST":
        form = ContactGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Group created successfully!")
            return redirect("group_list")
    else:
        form = ContactGroupForm()

    return render(request, "campaigns/group_form.html", {
        "form": form,
        "title": "Create Contact Group"
    })


def group_edit(request, pk):
    group = get_object_or_404(ContactGroup, pk=pk)

    if request.method == "POST":
        form = ContactGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated successfully!")
            return redirect("group_list")
    else:
        form = ContactGroupForm(instance=group)

    return render(request, "campaigns/group_form.html", {
        "form": form,
        "title": "Edit Contact Group"
    })


def group_delete(request, pk):
    group = get_object_or_404(ContactGroup, pk=pk)

    if request.method == "POST":
        group.delete()
        messages.success(request, "Group deleted successfully!")
        return redirect("group_list")

    return render(request, "campaigns/group_confirm_delete.html", {
        "group": group
    })

def email_logs(request):
    logs = EmailLog.objects.select_related("campaign").order_by("-sent_at")
    return render(request,"campaigns/email_logs.html",{"logs": logs})

# EMAIL TEMPLATE MANAGEMENT

def template_list(request):
    templates = EmailTemplate.objects.all().order_by("-created_at")

    return render(request, "campaigns/template_list.html", {
        "templates": templates
    })


def template_create(request):
    if request.method == "POST":
        form = EmailTemplateForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Email template created successfully!")
            return redirect("template_list")
    else:
        form = EmailTemplateForm()

    return render(request, "campaigns/template_form.html", {
        "form": form,
        "title": "Create Email Template"
    })


def template_edit(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)

    if request.method == "POST":
        form = EmailTemplateForm(request.POST, instance=template)

        if form.is_valid():
            form.save()
            messages.success(request, "Email template updated successfully!")
            return redirect("template_list")
    else:
        form = EmailTemplateForm(instance=template)

    return render(request, "campaigns/template_form.html", {
        "form": form,
        "title": "Edit Email Template"
    })


def template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)

    if request.method == "POST":
        template.delete()
        messages.success(request, "Email template deleted successfully!")
        return redirect("template_list")

    return render(request, "campaigns/template_confirm_delete.html", {
        "template": template
    })

def get_template_details(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)

    return JsonResponse({
        "subject": template.subject,
        "body": template.body
    })

def workflow_create(request):

    if request.method == "POST":
        form = WorkflowForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Workflow created successfully!"
            )

            return redirect("workflow_list")

    else:
        form = WorkflowForm()

    return render(
        request,
        "campaigns/workflow_form.html",
        {"form": form}
    )

def workflow_list(request):

    workflows = Workflow.objects.order_by("-created_at")

    return render(
        request,
        "campaigns/workflow_list.html",
        {"workflows": workflows}
    )

def workflow_edit(request, pk):

    workflow = get_object_or_404(Workflow, pk=pk)

    if request.method == "POST":
        form = WorkflowForm(request.POST, instance=workflow)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Workflow updated successfully!"
            )

            return redirect("workflow_list")

    else:
        form = WorkflowForm(instance=workflow)

    return render(
        request,
        "campaigns/workflow_form.html",
        {"form": form}
    )

def workflow_delete(request, pk):

    workflow = get_object_or_404(Workflow, pk=pk)

    if request.method == "POST":
        workflow.delete()

        messages.success(
            request,
            "Workflow deleted successfully!"
        )

        return redirect("workflow_list")

    return render(
        request,
        "campaigns/workflow_confirm_delete.html",
        {"workflow": workflow}
    )

def workflow_toggle(request, pk):

    workflow = get_object_or_404(Workflow, pk=pk)

    if request.method == "POST":

        workflow.is_active = not workflow.is_active
        workflow.save()

        messages.success(
            request,
            "Workflow status updated successfully!"
        )
    return redirect("workflow_list")

def clear_all_logs(request):

    if request.method == "POST":
        deleted_count, _ = EmailLog.objects.all().delete()

        messages.success(
            request,
            f"{deleted_count} email logs cleared successfully!"
        )

    return redirect("email_logs")