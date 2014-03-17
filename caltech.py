#!/usr/bin/env python

import datetime
import sys
from urllib import request

from bs4 import BeautifulSoup


CALTECH_URL = 'https://hr.caltech.edu/perks/time_away/holiday_observances'

MONTHS = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


def icalendar_date(date_time, full=False):
    text = '{:04}{:02}{:02}'.format(
        date_time.year,
        date_time.month,
        date_time.day
    )

    if full:
        text += 'T{:02}{:02}{:02}Z'.format(
            date_time.hour,
            date_time.minute,
            date_time.second
        )

    return text


def parse_date(text, year):
    """Parse month day text and return datetime object.

    Return None if text is not a date.

    """
    values = text.split()
    if len(values) != 2:
        return None

    month = MONTHS.get(values[0])
    if not month:
        return None

    return datetime.datetime(year, month, int(values[1]))


def main():
    soup = BeautifulSoup(request.urlopen(CALTECH_URL))

    print("""\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:caltech.py\
""")

    now = datetime.datetime.now()

    for row in soup.html.body.find('table').find_all('tr'):
        columns = [value.text for value in row.find_all('td')]
        start = parse_date(columns[2], year=now.year)
        if not start:
            continue
        end = start + datetime.timedelta(days=1)
        name = columns[3]
        print("""\
BEGIN:VEVENT
DTSTAMP:{now}
DTSTART:{start}
DTEND:{end}
SUMMARY:{name}
END:VEVENT\
""".format(now=icalendar_date(now, full=True),
           start=icalendar_date(start),
           end=icalendar_date(end),
           name=name))

    print("""\
END:VCALENDAR\
""")


if __name__ == '__main__':
    sys.exit(main())
