import re
import datetime

J2000 = datetime.datetime(2000, 1, 1, 12)


def to_human_time(seconds):
    """Convert a timespan in seconds into a human-readable format"""
    return str(datetime.timedelta(seconds=seconds))


def from_human_time(formatted_time):
    """Convert a timespan in a human-readable format into seconds"""
    regex = re.compile(
        r"(?:(\d+) days?, )?"  # days
        r"(\d+):(\d+):(\d+(?:\.\d+)?)"  # hours:minutes:seconds.fraction
    )
    m = regex.match(formatted_time)
    r = [float(x) for x in m.groups()]
    d = datetime.timedelta(days=r[0], hours=r[1], minutes=r[2], seconds=r[3])
    return d.total_seconds()


def to_human_date(seconds):
    """Convert a date from seconds since J2000 into a human-readable format"""
    return str(J2000 + datetime.timedelta(seconds=seconds))


def from_human_date(formatted_date):
    """Convert a date from a human-readable format into seconds since J2000"""
    truncated, _, second_fraction = formatted_date.partition('.')
    microsecond = int(float('0.' + second_fraction) * 1e6)
    d = datetime.datetime.strptime(truncated, '%Y-%m-%d %H:%M:%S')
    d = d.replace(microsecond=microsecond)
    d = d - J2000
    return d.total_seconds()


def to_kerbal_time(seconds):
    """Convert a timespan in seconds into a kerbal-readable format"""
    sign = "-" if seconds < 0 else "+"
    s = abs(float(seconds))
    m, s = divmod(s, 60)  # minutes
    h, m = divmod(m, 60)  # hours
    d, h = divmod(h, 6)  # days
    y, d = divmod(d, 426)  # years
    return sign + "%.5gy, %ud, %1u:%02u:%04.1f" % (y, d, h, m, s)


def from_kerbal_time(formatted_time):
    """Convert a timespan from a kerbal-readable format to seconds"""
    regex = re.compile(
        r"([+-])(\d+)y, "  # years
        r"(\d+)d, "  # days
        r"(\d+):(\d+):(\d+(?:\.\d+)?)"  # hours:minutes:seconds.fraction
    )
    match = regex.match(formatted_time)
    groups = match.groups()
    y, d, h, m, s = (float(group) if group else 0 for group in groups[1:])

    d += y * 426  # days
    h += d * 6  # hours
    m += h * 60  # minutes
    s += m * 60  # seconds
    return -s if groups[0] == "-" else s


def to_kerbal_date(seconds):
    """Convert a date from seconds since epoch into a kerbal-readable format"""
    return to_kerbal_time(seconds)


def from_kerbal_date(formatted_date):
    """Convert a date from a kerbal-readable format into seconds since epoch"""
    return from_kerbal_time(formatted_date)
