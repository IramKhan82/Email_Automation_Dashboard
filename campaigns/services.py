from django.core.mail import send_mail
from .models import Contact, EmailLog


def send_campaign_emails(campaign):

    campaign.status = "sending"
    campaign.save(update_fields=["status"])

    recipient_ids = set(
        campaign.recipients.filter(
            is_active=True
        ).values_list("id", flat=True)
    )

    for group in campaign.groups.all():
        group_contact_ids = group.contacts.filter(
            is_active=True
        ).values_list("id", flat=True)

        recipient_ids.update(group_contact_ids)

    recipients = Contact.objects.filter(
        id__in=recipient_ids,
        is_active=True
    )

    sent_count = 0
    failed_count = 0

    for contact in recipients:
        try:
            result = send_mail(
                subject=campaign.subject,
                message=campaign.body,
                from_email=None,
                recipient_list=[contact.email],
                fail_silently=False,
            )

            if result == 1:
                EmailLog.objects.create(
                    campaign=campaign,
                    recipient_email=contact.email,
                    status="sent",
                )
                sent_count += 1

            else:
                raise Exception("Email was not sent.")

        except Exception as e:
            EmailLog.objects.create(
                campaign=campaign,
                recipient_email=contact.email,
                status="failed",
                error_message=str(e),
            )

            failed_count += 1

    campaign.status = "sent" if sent_count > 0 else "failed"
    campaign.save(update_fields=["status"])

    return sent_count, failed_count