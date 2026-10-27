from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ExternalRef


def find_entity_id(session: Session, provider: str, entity_type: str, external_id: str) -> int | None:
    return session.scalars(
        select(ExternalRef.entity_id).where(
            ExternalRef.provider == provider,
            ExternalRef.entity_type == entity_type,
            ExternalRef.external_id == external_id,
        )
    ).first()


def add_ref(
    session: Session, provider: str, entity_type: str, entity_id: int, external_id: str
) -> None:
    session.add(
        ExternalRef(
            provider=provider, entity_type=entity_type, entity_id=entity_id, external_id=external_id
        )
    )
    session.flush()
