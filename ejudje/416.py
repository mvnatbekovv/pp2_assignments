import sys
from datetime import datetime, timedelta, timezone

def parse_dt(line: str) -> datetime:
    date_part, time_part, tz_part = line.strip().split()
    y, m, d = map(int, date_part.split('-'))
    hh, mm, ss = map(int, time_part.split(':'))

    sign = 1 if tz_part[3] == '+' else -1
    tz_h = int(tz_part[4:6])
    tz_m = int(tz_part[7:9])
    tz = timezone(sign * timedelta(hours=tz_h, minutes=tz_m))

    dt = datetime(y, m, d, hh, mm, ss, tzinfo=tz)
    return dt.astimezone(timezone.utc)

start_utc = parse_dt(sys.stdin.readline())
end_utc = parse_dt(sys.stdin.readline())

duration = int((end_utc - start_utc).total_seconds())
print(duration)