from datetime import timedelta
PREBUILT = dict(
    hour=timedelta(hours=1),
    day=timedelta(days=1),
    week=timedelta(weeks=1),
    month=timedelta(days=30),
    quarter=timedelta(weeks=16),
    year=timedelta(days=365)
)
