from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List

import httpx

from ics import Calendar

from .base import IEvent, IImporter, IImporterBuilder


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
            try:
                with httpx.Client() as client:
                    resp = client.get(self._path)
                    resp.raise_for_status()
                    data = resp.text
            except httpx.HTTPError as e:
                print("--- ICS network failure ---")
                req = e.request
                print("Request URL:", str(req.url))
                print("Request headers:", dict(req.headers))
                if req.content:
                    print(
                        "Request payload:",
                        req.content.decode("utf-8", errors="replace"),
                    )
                else:
                    print("Request payload: <none>")
                if isinstance(e, httpx.HTTPStatusError):
                    resp = e.response
                    print("Response code:", resp.status_code)
                    print("Response headers:", dict(resp.headers))
                    print("Response payload:", resp.text)
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
        for ev in self._events:
            ev_start, ev_end = ev.GetTime()
            if ev_end >= start and ev_start <= end:
                yield ev


class ICSImportBuilder(IImporterBuilder):
    def __init__(self) -> None:
        self._path = ""

    def path(self, path: str) -> "ICSImportBuilder":
        self._path = path
        return self

    def Build(self) -> IImporter:
        return ICSImporter(self._path)
