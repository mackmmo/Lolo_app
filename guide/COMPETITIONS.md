# Publication and competitions

Profile has independent feed and leaderboard/Hall of Fame permissions. All public queries enforce them on the server; turning them off retains private logs. Existing users retain feed publication during migration, with leaderboard participation off. Leaderboard sharing is opt-in. Migration 0003 is a compatibility placeholder and no longer enrolls users automatically. If its earlier version was already applied, existing saved permissions remain; users can change them in Profile. New users start with both off. Private beta, email and attempts are never published.

JuntMasters uses America/Denver calendar years. A send needs date_sent; its Date sent determines the competition year, including backlogged sends. The time it was entered or updated does not affect eligibility. Each user/route/year is unique. Grade index is the point value; equal totals share rank. All-Time requires a date and counts each user/route once overall. The route guide supports another dated send plus editing/deleting annual history.

JuntMasters begins in 2026. Junts Hall of Fame shows rank-one finishers of completed seasons from 2026 onwards, including ties. Completed standings retain their points/ranks after archiving, and publication permission still controls visibility. Opting out hides an archived winner without promoting the next finisher.

## Deployment

Deploy the backend and run `python manage.py migrate` before publishing this frontend. Migration 0001 records the existing guide/route_log/route_todo/route_comment tables as state only; it does not recreate existing spatial tables. Migration 0002 creates publication settings, annual sends, seasons and standings and imports existing dated sends. These migrations assume the existing legacy tables already exist; they do not initialize an empty database.

Run `python manage.py finalize_juntmasters` just after New Year in America/Denver to archive final standings promptly. Configure this command in the hosting scheduler. A request for a past-year board or Hall of Fame also finalizes any missing completed season on demand. Before the first archival run, results use the then-current grade indexes and publication settings; an end-of-year scheduler prevents later changes from influencing that first snapshot.

Local verification uses a temporary SQLite database with geometry fields substituted for text. It checks migration/backfill, publication opt-out, deduplication, date eligibility, ties, snapshot stability, API authentication/ownership and source-log synchronization. Mobile UI checks use mocked API responses. Production PostGIS/GDAL integration and deployment remain to be verified on the host.
