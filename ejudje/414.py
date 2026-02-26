import sys
from datetime import datetime, timedelta

def parse_date(line: str) -> datetime:
    date_part, tz_part = line.strip().split()
    year, month, day = map(int, date_part.split('-'))

    sign = 1 if tz_part[3] == '+' else -1
    h, m = map(int, tz_part[4:].split(':'))
    offset_seconds = sign * (h * 3600 + m * 60)

    local_midnight = datetime(year, month, day)
    utc = local_midnight - timedelta(seconds=offset_seconds)
    return utc

t1 = parse_date(sys.stdin.readline())
t2 = parse_date(sys.stdin.readline())

diff_days = abs((t1 - t2).total_seconds()) // 86400
print(int(diff_days))