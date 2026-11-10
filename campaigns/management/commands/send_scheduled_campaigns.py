from django.core.management.base import BaseCommand
from django.utils import timezone

from campaigns.models import Campaign
from campaigns.services import send_campaign_emails


class Command(BaseCommand):
    help = "Send all campaigns whose scheduled time has arrived"

    def handle(self, *args, **kwargs):

        current_time = timezone.now()

        campaigns = Campaign.objects.filter(
            status="scheduled",
            scheduled_at__lte=current_time
        )
        self.stdout.write(f"Found campaigns: {campaigns.count()}")

        for campaign in campaigns:

            self.stdout.write(
                f"Sending campaign: {campaign.name}"
            )

            sent_count, failed_count = send_campaign_emails(campaign)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Completed: {campaign.name} | "
                    f"Sent: {sent_count} | Failed: {failed_count}"
                )
            )