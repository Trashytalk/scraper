"""Pydantic models for API requests and responses."""

from __future__ import annotations

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int

    class Config:
        orm_mode = True


class HealthCheckResponse(BaseModel):
    """Response model for the root health check endpoint."""

    message: str
    database_url: str


class TaskCreateResponse(BaseModel):
    """Response model returned when a scraping task is created."""

    task_id: str


class TaskStatusResponse(BaseModel):
    """Response model for checking task status."""

    status: str


class JobStatus(BaseModel):
    """Status of a background job."""

    status: str
