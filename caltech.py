#!/usr/bin/env python3

import datetime
import html.parser
import sys
import urllib.request


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


class CalendarParser(html.parser.HTMLParser):

    tables = []

    _in_table = False
    _in_tr = False
    _in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table' and not self._in_table:
            self.tables.append([])
            self._in_table = True

        if tag == 'tr' and self._in_table:
            self.tables[-1].append([])
            self._in_tr = True

        if tag == 'td' and self._in_tr:
            self._in_td = True

    def handle_endtag(self, tag):
        if tag == 'table':
            self._in_table = False

        if tag == 'tr':
            self._in_tr = False

        if tag == 'td':
            self._in_td = False

    def handle_data(self, data):
        if self._in_td:
            self.tables[-1][-1].append(data)


def yield_normalized_colummns(columns):
    for col in columns:
        if col.strip():
            yield col


def main():
    with urllib.request.urlopen(CALTECH_URL) as input_file:
        last_modified = datetime.datetime.strptime(
            input_file.info()['Last-Modified'],
            '%a, %d %b %Y %H:%M:%S %Z')
        text = input_file.read().decode(
            input_file.headers.get_content_charset())

        calendar_parser = CalendarParser()
        calendar_parser.feed(text)

    all_years = [year for year in range(last_modified.year - 10,
                                        last_modified.year + 10)
                 if 'for {}'.format(year) in text.lower()]

    assert len(calendar_parser.tables) == len(all_years)

    print(HEADER)

    for (year, table) in zip(all_years, calendar_parser.tables):
        for columns in table:
            columns = list(yield_normalized_colummns(columns))
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
