from app.models import Event
from app.schemas.catalog import CompetitionRef
from app.schemas.events import EventSummary, ParticipantOut


def event_summary_fields(event: Event) -> dict:
    competition = event.season.competition
    return {
        "id": event.id,
        "start_time": event.start_time,
        "status": event.status,
        "round": event.round,
        "venue_name": event.venue_name,
        "venue_city": event.venue_city,
        "sport": competition.sport.slug,
        "competition": CompetitionRef(id=competition.id, name=competition.name),
        "season": event.season.label,
    }


def to_summary(event: Event) -> EventSummary:
    return EventSummary(
        **event_summary_fields(event),
        participants=[ParticipantOut.model_validate(p, from_attributes=True) for p in event.participants],
    )
