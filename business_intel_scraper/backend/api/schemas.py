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
