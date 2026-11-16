"""Models package — imports all ORM models so Alembic can discover them."""
from app.models.user import User, UserRole  # noqa: F401
from app.models.faculty import Faculty, Department  # noqa: F401
from app.models.publication import (  # noqa: F401
    Publication,
    PublicationAuthor,
    PublicationSource,
)
from app.models.verification import PublicationVerification  # noqa: F401
from app.models.duplicate import DuplicateCandidate  # noqa: F401
from app.models.citation import CitationSnapshot  # noqa: F401
from app.models.agent import AgentExecution, AgentLog  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.report import Report  # noqa: F401
