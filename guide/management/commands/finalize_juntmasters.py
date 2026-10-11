from django.core.management.base import BaseCommand
from guide.competition import competition_today, finalize_season
from guide.models import CompetitionSend


class Command(BaseCommand):
    help = "Archive completed JuntMasters seasons. Run after New Year in America/Denver."

    def handle(self, *args, **options):
        years = CompetitionSend.objects.filter(year__lt=competition_today().year).values_list("year", flat=True).distinct()
        for year in years:
            season = finalize_season(year)
            self.stdout.write(f"JuntMasters {year} archived at {season.finalized_at}")
