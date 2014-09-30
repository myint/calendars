#!/usr/bin/env python

import datetime
import sys
from urllib import request

import bs4


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

HEADER = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:caltech.py\
"""

FOOTER = 'END:VCALENDAR'


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
    with request.urlopen(CALTECH_URL) as input_file:
        last_modified = datetime.datetime.strptime(
            input_file.info()['Last-Modified'],
            '%a, %d %b %Y %H:%M:%S %Z')

        soup = bs4.BeautifulSoup(input_file)

    body = soup.html.body

    all_years = [year for year in range(last_modified.year - 1,
                                        last_modified.year + 3)
                 if 'for {}'.format(year) in body.text.lower()]

    all_tables = body.find_all('table')
    assert len(all_tables) == len(all_years)

    print(HEADER)

    for (year, table) in zip(all_years, all_tables):
        for row in table.find_all('tr'):
            columns = [value.text for value in row.find_all('td')]

            start = parse_date(columns[2], year=year)
            if not start:
                continue

            end = start + datetime.timedelta(days=1)
            name = columns[3]

            print("""\
BEGIN:VEVENT
DTSTAMP:{last_modified}
DTSTART:{start}
DTEND:{end}
SUMMARY:{name}
END:VEVENT\
""".format(last_modified=icalendar_date(last_modified, full=True),
           start=icalendar_date(start),
           end=icalendar_date(end),
           name=name))

    print(FOOTER)


if __name__ == '__main__':
    sys.exit(main())
