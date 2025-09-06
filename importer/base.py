from __future__ import annotations

import abc
import datetime as dt
from typing import Iterable, List


class IEvent(abc.ABC):
    """Represents a calendar event."""

    @abc.abstractmethod
    def GetTime(self) -> tuple[dt.datetime, dt.datetime]:
        """Return start and end time of the event (tz-aware)."""

    @abc.abstractmethod
    def GetTitle(self) -> str:
        """Return event title."""

    @abc.abstractmethod
    def GetDetail(self) -> str:
        """Return event detail/description."""


class IImporter(abc.ABC):
    """Importer capable of loading events."""

    @abc.abstractmethod
    def Load(self) -> None:
        """Fetch and store data necessary for importing."""

    @abc.abstractmethod
    def LoadRange(self, start: dt.datetime, end: dt.datetime) -> Iterable[IEvent]:
        """Yield events that overlap with the given time range."""


class IImporterBuilder(abc.ABC):
    """Builder creating an :class:`IImporter`."""

    @abc.abstractmethod
    def Build(self) -> IImporter:
        """Construct the configured importer."""


def build_importers(configs: List[dict]) -> List[IImporter]:
    """Factory creating importers from configuration dictionaries."""
    from .ics import ICSImportBuilder

    result: List[IImporter] = []
    for cfg in configs or []:
        importer_type = cfg.get("importer_type")
        if importer_type == "ics":
            builder = ICSImportBuilder().path(cfg.get("path", ""))
            result.append(builder.Build())
        else:
            raise ValueError(f"Unsupported importer type: {importer_type}")
    return result
