"""Calendar-year competitions and server-side publication controls."""
from datetime import date, datetime
from zoneinfo import ZoneInfo
from django.utils import timezone
from django.db import transaction
from .models import CompetitionSend, RouteLog, JuntMastersSeason, JuntMastersStanding

COMPETITION_ZONE = ZoneInfo("America/Denver")


def competition_today():
    return timezone.localdate(timezone=COMPETITION_ZONE)


def recorded_year(timestamp):
    return timezone.localtime(timestamp, COMPETITION_ZONE).year


def sync_competition_send(log, previous_year=None):
    if log.status != "sent" or not log.date_sent:
        CompetitionSend.objects.filter(source_log=log).delete()
        return
    year = log.date_sent.year
    if previous_year and previous_year != year:
        previous = CompetitionSend.objects.filter(source_log=log, year=previous_year)
        if previous_year < competition_today().year and year == competition_today().year:
            # A repeat this year retains the earlier year's historical send.
            previous.update(source_log=None)
        else:
            previous.delete()
    send, created = CompetitionSend.objects.get_or_create(
        user=log.user, route=log.route, year=year,
        defaults={"date_sent": log.date_sent, "send_style": log.send_style, "source_log": log},
    )
    if not created and send.source_log_id == log.pk:
        send.date_sent = log.date_sent
        send.send_style = log.send_style
        send.save(update_fields=["date_sent", "send_style"])


def public_feed_entries(route_id=None):
    published = {"user__data_permissions__publish_feed": True, "user__is_active": True}
    sends = CompetitionSend.objects.filter(**published).select_related("user", "route")
    logs = RouteLog.objects.filter(status="sent", **published).select_related("user", "route")
    if route_id is not None:
        sends = sends.filter(route_id=route_id)
        logs = logs.filter(route_id=route_id)
    entries = []
    seen = set()
    for send in sends:
        seen.add((send.user_id, send.route_id, send.year))
        entries.append(feed_entry(send))
    for log in logs:
        key = (log.user_id, log.route_id, log.date_sent.year if log.date_sent else None)
        if key not in seen:
            entries.append(feed_entry(log))
    entries.sort(key=lambda entry: (entry["date_sent"] or "", entry["created_at"]), reverse=True)
    return entries


def feed_entry(send):
    return {
        "username": send.user.username, "route_id": send.route_id,
        "route_name": send.route.name, "grade": send.route.grade,
        "send_style": send.send_style, "date_sent": send.date_sent.isoformat() if send.date_sent else None,
        "created_at": (getattr(send, "recorded_at", None) or send.created_at).isoformat(),
    }


def rank_route_points(rows):
    """Rows are (user id, username, route id, points); never count a route twice."""
    users = {}
    for user_id, username, route_id, points in rows:
        user = users.setdefault(user_id, {"username": username, "routes": {}})
        user["routes"][route_id] = points or 0
    ranked = sorted(({**value, "user_id": key} for key, value in users.items()), key=lambda user: (-sum(user["routes"].values()), user["username"].casefold()))
    entries = []
    previous_points = None
    rank = 0
    for position, user in enumerate(ranked, 1):
        points = sum(user["routes"].values())
        if points != previous_points:
            rank = position
        entries.append({"user_id": user["user_id"], "rank": rank, "username": user["username"], "points": points, "route_count": len(user["routes"])})
        previous_points = points
    return entries


def live_leaderboard_entries(board, year):
    published = {"user__data_permissions__publish_leaderboards": True, "user__is_active": True}
    today = competition_today()
    sends = CompetitionSend.objects.filter(date_sent__lte=today, **published)
    if board == "juntmasters":
        start = datetime(year, 1, 1, tzinfo=COMPETITION_ZONE)
        end = datetime(year + 1, 1, 1, tzinfo=COMPETITION_ZONE)
        sends = sends.filter(year=year, date_sent__year=year, recorded_at__gte=start, recorded_at__lt=end)
    rows = list(sends.values_list("user_id", "user__username", "route_id", "route__grade_index"))
    if board == "alltime":
        # Dated legacy sends remain eligible even before annual logging was introduced.
        rows.extend(RouteLog.objects.filter(status="sent", date_sent__isnull=False, date_sent__lte=today, **published).values_list("user_id", "user__username", "route_id", "route__grade_index"))
    return rank_route_points(rows)


@transaction.atomic
def finalize_season(year):
    if year >= competition_today().year:
        raise ValueError("Only completed years can be archived.")
    season, _ = JuntMastersSeason.objects.get_or_create(year=year)
    season = JuntMastersSeason.objects.select_for_update().get(pk=season.pk)
    if season.finalized_at is None:
        entries = live_leaderboard_entries("juntmasters", year)
        JuntMastersStanding.objects.bulk_create([
            JuntMastersStanding(season=season, user_id=entry["user_id"], rank=entry["rank"],
                               points=entry["points"], route_count=entry["route_count"])
            for entry in entries
        ])
        season.finalized_at = timezone.now()
        season.save(update_fields=["finalized_at"])
    return season


def archived_entries(season, winners_only=False):
    standings = season.standings.filter(user__is_active=True, user__data_permissions__publish_leaderboards=True)
    if winners_only:
        standings = standings.filter(rank=1)
    return list(standings.order_by("rank", "user__username").values(
        "user_id", "rank", "points", "route_count", username=models_username_expression()))


def models_username_expression():
    from django.db.models import F
    return F("user__username")


def leaderboard_entries(board, year):
    if board == "juntmasters" and year < competition_today().year:
        return archived_entries(finalize_season(year))
    return live_leaderboard_entries(board, year)


def hall_of_fame():
    years = set(CompetitionSend.objects.filter(year__lt=competition_today().year).values_list("year", flat=True))
    years.update(JuntMastersSeason.objects.values_list("year", flat=True))
    return [{"year": year, "winners": archived_entries(finalize_season(year), winners_only=True)}
            for year in sorted(years, reverse=True)]
