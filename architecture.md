# Architecture Overview

## Importer Interfaces

Importers provide events from external sources and follow a small set of
interfaces.

### `IEvent`

Represents a calendar event.  It exposes:

* `GetTime() -> tuple[datetime, datetime]` – returns the start and end time of
  the event.  Times are timezone‑aware.
* `GetTitle() -> str` – short title of the event.
* `GetDetail() -> str` – full description of the event.

### `IImporter`

Responsible for fetching and serving events.

* `Load() -> None` – called once at program start to download or read any data
  the importer needs.
* `LoadRange(start, end) -> Iterable[IEvent]` – yields all events that overlap
  with the requested time range.

### `IImporterBuilder`

A builder object that configures importer instances.  Each concrete importer
exposes configuration helpers and a final `Build()` method returning an
`IImporter`.

## ICS Importer

The first concrete importer reads from an `.ics` file available either locally
or over HTTP.

* `ICSImportBuilder.path(str)` – sets the path or URL of the ICS file.
* `ICSImporter` downloads the data in `Load()` and keeps parsed events
  internally.
* `LoadRange()` filters the stored events and yields them as `IEvent`
  instances.

## Configuration

YAML preset files accept an `importers` section:

```yaml
mode: weekly
importers:
  - importer_type: ics
    path: "https://www.lwsd.org/calendar/calendar_354.ics"
```

Each list item describes one importer.  The field `importer_type` selects the
implementation.  Additional fields are importer specific; for the ICS importer
it requires `path`.
