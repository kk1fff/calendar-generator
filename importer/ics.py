from __future__ import annotations

import calendar
import datetime as dt
import io
import contextlib
import subprocess
from dataclasses import dataclass
from typing import Iterable, List
from urllib import error, request

from ics import Calendar

from .base import IEvent, IImporter, IImporterBuilder


def _wget_user_agent() -> str:
    """Return a user-agent string matching the locally installed wget."""
    try:
        # Output begins with: 'GNU Wget 1.21.4 built on ...'
        result = subprocess.run(
            ["wget", "--version"], capture_output=True, text=True, check=True
        )
        version = result.stdout.splitlines()[0].split()[2]
        return f"Wget/{version}"
    except Exception:
        # Fallback to a commonly used wget version if detection fails.
        return "Wget/1.21.4"


@dataclass
class ICSEvent(IEvent):
    _start: dt.datetime
    _end: dt.datetime
    _title: str
    _detail: str

    def GetTime(self) -> tuple[dt.datetime, dt.datetime]:
        return self._start, self._end

    def GetTitle(self) -> str:
        return self._title

    def GetDetail(self) -> str:
        return self._detail


class ICSImporter(IImporter):
    def __init__(self, path: str) -> None:
        self._path = path
        self._events: List[ICSEvent] = []

    def Load(self) -> None:
        if self._path.startswith("http://") or self._path.startswith("https://"):
            req = request.Request(self._path, headers={"User-Agent": _wget_user_agent()})
            opener = request.build_opener(
                request.HTTPHandler(debuglevel=1),
                request.HTTPSHandler(debuglevel=1),
            )
            network_log = io.StringIO()
            try:
                with contextlib.redirect_stderr(network_log):
                    with opener.open(req) as resp:
                        data = resp.read().decode("utf-8")
            except Exception as e:
                print("--- ICS network failure ---")
                print("Request URL:", req.full_url)
                print("Request headers:", dict(req.header_items()))
                if req.data:
                    print(
                        "Request payload:",
                        req.data.decode("utf-8", errors="replace"),
                    )
                else:
                    print("Request payload: <none>")
                print("Network detail:")
                print(network_log.getvalue())
                if isinstance(e, error.HTTPError):
                    print("Response code:", e.code)
                    print("Response headers:", dict(e.headers.items()))
                    try:
                        resp_payload = e.read().decode("utf-8", errors="replace")
                    except Exception:
                        resp_payload = "<unable to read response payload>"
                    print("Response payload:", resp_payload)
                print("Error summary:", repr(e))
                raise
        else:
            with open(self._path, "r", encoding="utf-8") as f:
                data = f.read()
        cal = Calendar(data)
        self._events = [
            ICSEvent(
                e.begin.datetime,
                e.end.datetime,
                e.name or "",
                e.description or "",
            )
            for e in cal.events
        ]

    def LoadRange(self, start: dt.datetime, end: dt.datetime) -> Iterable[IEvent]:
        year = start.year
        is_leap = calendar.isleap(year)
        for ev in self._events:
            ev_start, ev_end = ev.GetTime()
            if ev_end >= start and ev_start <= end:
                yield ev
            elif (
                not is_leap
                and ev_start.month == 2
                and ev_start.day == 29
            ):
                duration = ev_end - ev_start
                adjusted_start = ev_start.replace(year=year, day=28)
                adjusted_end = adjusted_start + duration
                if adjusted_end >= start and adjusted_start <= end:
                    yield ICSEvent(
                        adjusted_start,
                        adjusted_end,
                        ev.GetTitle(),
                        ev.GetDetail(),
                    )


class ICSImportBuilder(IImporterBuilder):
    def __init__(self) -> None:
        self._path = ""

    def path(self, path: str) -> "ICSImportBuilder":
        self._path = path
        return self

    def Build(self) -> IImporter:
        return ICSImporter(self._path)
