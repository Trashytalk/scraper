from typing import Any

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from strawberry import ID

# Type alias for mypy
JSONType = Any

from . import main as api
from ..workers.tasks import get_task_status


@strawberry.type
class Job:
    """Background job status."""

    id: ID
    status: str


@strawberry.type
class Query:
    """GraphQL queries for scraped data and jobs."""

    @strawberry.field
    def scraped_data(
        self, search: str | None = None, limit: int | None = None
    ) -> list[Any]:
        """Return scraped items, optionally filtered by a search term."""

        data = api.scraped_data
        if search:
            lowered = search.lower()
            data = [
                item
                for item in data
                if any(lowered in str(value).lower() for value in item.values())
            ]
        if limit is not None:
            data = data[:limit]
        return data

    @strawberry.field
    def job(self, id: ID) -> Job | None:
        """Return a single job by ID."""

        status = api.jobs.get(str(id))
        if status is None:
            return None
        # Handle both dict and string status types
        status_str = status.get("status", "unknown") if isinstance(status, dict) else str(status)  # type: ignore[unreachable]
        return Job(id=id, status=status_str)

    @strawberry.field
    def jobs(self) -> list[Job]:
        """Return all known jobs."""

        return [Job(id=ID(jid), status=get_task_status(jid)) for jid in list(api.jobs)]


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
