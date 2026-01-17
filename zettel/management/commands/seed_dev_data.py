# core/management/commands/seed_dev_data.py

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from zettel.models import Kandidatur

User = get_user_model()


class Command(BaseCommand):
    help = "Seed dummy data for development only"

    def handle(self, *args, **options):
        # 🔒 Safety guard
        if os.getenv("DJANGO_ENV") != "dev":
            self.stderr.write("Sind nicht in dev-modus, also keine dummydaten")
            return

        self.stdout.write("Schreibe dummydaten...")

        for postenname in ("Gremium 1", "Gremium 2", "Gremium 3"):
            for vorname in ("Tick", "Trick", "Track"):
                Kandidatur.objects.get_or_create(
                    gewaehlt="noch nicht",
                    bestaetigt="ja",
                    gremium=postenname,
                    first_name=vorname,
                    last_name="Duck",
                    fakultaetFachschaft="Beispielanmerkung",
                    lesung="Standardlesung",
                )

        self.stdout.write(self.style.SUCCESS("Dummydaten geschrieben"))
