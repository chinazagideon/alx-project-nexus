from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Command to check the health of the application
    """
    help = "Simple health check"

    def handle(self, *args, **opts):
        """
        Handle the health check
        """
        self.stdout.write(self.style.SUCCESS("OK"))
