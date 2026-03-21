"""Google Calendar provider using Google Calendar API v3."""

from datetime import datetime

from ..config.settings import CalendarSettings
from ..exceptions import CalendarAuthError, CalendarSyncError
from ..schemas.event import CalendarEvent, EventCreate, EventUpdate


class GoogleCalendarProvider:
    """Google Calendar API v3 provider.

    Requires the 'google' optional dependency:
        pip install ulfblk-calendar[google]

    Google API libraries are imported lazily inside each method so that the
    package can be imported without the optional dependency installed.

    Example::

        settings = CalendarSettings(
            google_credentials_path="/path/to/credentials.json",
            google_calendar_id="primary",
        )
        provider = GoogleCalendarProvider(settings)
        events = await provider.list_events(start, end)
    """

    def __init__(self, settings: CalendarSettings) -> None:
        self._settings = settings
        self._service = None

    def _get_service(self):
        """Build and cache the Google Calendar API service.

        Returns:
            The Google Calendar API service resource.

        Raises:
            CalendarAuthError: If credentials cannot be loaded or are invalid.
        """
        if self._service is not None:
            return self._service

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            if not self._settings.google_credentials_path:
                raise CalendarAuthError("google_credentials_path is not configured")

            creds = Credentials.from_authorized_user_file(
                self._settings.google_credentials_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
            )
            self._service = build("calendar", "v3", credentials=creds)
            return self._service
        except ImportError:
            raise CalendarAuthError(
                "Google API libraries not installed. "
                "Install with: pip install ulfblk-calendar[google]"
            )
        except CalendarAuthError:
            raise
        except Exception as exc:
            raise CalendarAuthError(f"Failed to initialize Google Calendar service: {exc}")

    async def create_event(self, event: EventCreate) -> CalendarEvent:
        """Create a new event in Google Calendar.

        Args:
            event: The event data to create.

        Returns:
            The created event with the Google Calendar event ID.

        Raises:
            CalendarSyncError: If the API call fails.
        """
        try:
            from googleapiclient.errors import HttpError

            service = self._get_service()
            body = {
                "summary": event.title,
                "description": event.description,
                "location": event.location,
                "start": {
                    "dateTime": event.start.isoformat(),
                    "timeZone": self._settings.timezone,
                },
                "end": {
                    "dateTime": event.end.isoformat(),
                    "timeZone": self._settings.timezone,
                },
                "attendees": [{"email": a} for a in event.attendees],
            }
            result = (
                service.events()
                .insert(calendarId=self._settings.google_calendar_id, body=body)
                .execute()
            )
            return CalendarEvent(
                external_id=result["id"],
                title=result.get("summary", ""),
                start=event.start,
                end=event.end,
                description=result.get("description", ""),
                location=result.get("location", ""),
                attendees=[a.get("email", "") for a in result.get("attendees", [])],
            )
        except CalendarAuthError:
            raise
        except ImportError:
            raise CalendarSyncError(
                "Google API libraries not installed. "
                "Install with: pip install ulfblk-calendar[google]"
            )
        except Exception as exc:
            raise CalendarSyncError(f"Failed to create event: {exc}")

    async def update_event(self, event_id: str, event: EventUpdate) -> CalendarEvent:
        """Update an existing event in Google Calendar.

        Args:
            event_id: The Google Calendar event ID.
            event: The fields to update. Only non-None fields are sent.

        Returns:
            The updated event.

        Raises:
            CalendarSyncError: If the API call fails.
        """
        try:
            from googleapiclient.errors import HttpError

            service = self._get_service()
            body: dict = {}

            if event.title is not None:
                body["summary"] = event.title
            if event.description is not None:
                body["description"] = event.description
            if event.location is not None:
                body["location"] = event.location
            if event.start is not None:
                body["start"] = {
                    "dateTime": event.start.isoformat(),
                    "timeZone": self._settings.timezone,
                }
            if event.end is not None:
                body["end"] = {
                    "dateTime": event.end.isoformat(),
                    "timeZone": self._settings.timezone,
                }

            result = (
                service.events()
                .patch(
                    calendarId=self._settings.google_calendar_id,
                    eventId=event_id,
                    body=body,
                )
                .execute()
            )

            start_dt = event.start or datetime.fromisoformat(
                result["start"].get("dateTime", result["start"].get("date"))
            )
            end_dt = event.end or datetime.fromisoformat(
                result["end"].get("dateTime", result["end"].get("date"))
            )

            return CalendarEvent(
                external_id=result["id"],
                title=result.get("summary", ""),
                start=start_dt,
                end=end_dt,
                description=result.get("description", ""),
                location=result.get("location", ""),
                attendees=[a.get("email", "") for a in result.get("attendees", [])],
            )
        except CalendarAuthError:
            raise
        except ImportError:
            raise CalendarSyncError(
                "Google API libraries not installed. "
                "Install with: pip install ulfblk-calendar[google]"
            )
        except Exception as exc:
            raise CalendarSyncError(f"Failed to update event {event_id}: {exc}")

    async def delete_event(self, event_id: str) -> None:
        """Delete an event from Google Calendar.

        Args:
            event_id: The Google Calendar event ID.

        Raises:
            CalendarSyncError: If the API call fails.
        """
        try:
            from googleapiclient.errors import HttpError

            service = self._get_service()
            (
                service.events()
                .delete(calendarId=self._settings.google_calendar_id, eventId=event_id)
                .execute()
            )
        except CalendarAuthError:
            raise
        except ImportError:
            raise CalendarSyncError(
                "Google API libraries not installed. "
                "Install with: pip install ulfblk-calendar[google]"
            )
        except Exception as exc:
            raise CalendarSyncError(f"Failed to delete event {event_id}: {exc}")

    async def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """List events from Google Calendar within a time range.

        Args:
            start: The start of the time range.
            end: The end of the time range.

        Returns:
            A list of events within the specified range.

        Raises:
            CalendarSyncError: If the API call fails.
        """
        try:
            from googleapiclient.errors import HttpError

            service = self._get_service()
            result = (
                service.events()
                .list(
                    calendarId=self._settings.google_calendar_id,
                    timeMin=start.isoformat(),
                    timeMax=end.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = []
            for item in result.get("items", []):
                start_str = item["start"].get("dateTime", item["start"].get("date"))
                end_str = item["end"].get("dateTime", item["end"].get("date"))
                events.append(
                    CalendarEvent(
                        external_id=item["id"],
                        title=item.get("summary", ""),
                        start=datetime.fromisoformat(start_str),
                        end=datetime.fromisoformat(end_str),
                        description=item.get("description", ""),
                        location=item.get("location", ""),
                        attendees=[
                            a.get("email", "") for a in item.get("attendees", [])
                        ],
                    )
                )
            return events
        except CalendarAuthError:
            raise
        except ImportError:
            raise CalendarSyncError(
                "Google API libraries not installed. "
                "Install with: pip install ulfblk-calendar[google]"
            )
        except Exception as exc:
            raise CalendarSyncError(f"Failed to list events: {exc}")
