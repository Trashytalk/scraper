"""
Database compatibility utilities for handling JSONB/JSON differences between SQLite and PostgreSQL
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.sql import sqltypes

def get_json_type(engine: Engine = None) -> sqltypes.TypeEngine:
    """
    Returns appropriate JSON type based on database engine
    """
    if engine and 'sqlite' in engine.dialect.name:
        return JSON
    else:
        # Default to JSONB for PostgreSQL or if engine is not provided
        return JSONB

# Create a portable JSON type that works with both SQLite and PostgreSQL
class PortableJSON(sqltypes.TypeDecorator):
    """A portable JSON type that works with both SQLite and PostgreSQL"""
    
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())
