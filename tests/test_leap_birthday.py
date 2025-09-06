from __future__ import annotations
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import datetime as dt
from importer.ics import ICSImporter

def create_importer(tmp_path):
    ics_content = """BEGIN:VCALENDAR\nPRODID:-//Example//Test//EN\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART;VALUE=DATE:20240229\nRRULE:FREQ=YEARLY\nSUMMARY:Leap Day Birthday\nEND:VEVENT\nEND:VCALENDAR\n"""
    ics_file = tmp_path / "birthday.ics"
    ics_file.write_text(ics_content)
    imp = ICSImporter(str(ics_file))
    imp.Load()
    return imp


def test_leap_day_in_non_leap_year(tmp_path):
    imp = create_importer(tmp_path)
    start = dt.datetime(2023, 2, 28, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(days=1)
    events = list(imp.LoadRange(start, end))
    assert len(events) == 1
    ev_start, _ = events[0].GetTime()
    assert ev_start.date() == dt.date(2023, 2, 28)


def test_leap_day_in_leap_year(tmp_path):
    imp = create_importer(tmp_path)
    start = dt.datetime(2024, 2, 29, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(days=1)
    events = list(imp.LoadRange(start, end))
    assert len(events) == 1
    ev_start, _ = events[0].GetTime()
    assert ev_start.date() == dt.date(2024, 2, 29)
