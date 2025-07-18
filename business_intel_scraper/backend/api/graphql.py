import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from strawberry import ID

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
    ) -> list[JSON]:
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
        if isinstance(status, dict):
            status = status.get("status", "unknown")
        return Job(id=id, status=str(status))

    @strawberry.field
    def jobs(self) -> list[Job]:
        """Return all known jobs."""

        return [Job(id=jid, status=get_task_status(jid)) for jid in list(api.jobs)]


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
