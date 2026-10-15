from contextlib import nullcontext

from alembic import context

from app.config import database_url
from app.db.connection import build_engine
from app.db.models import Base

config = context.config
target_metadata = Base.metadata


if context.is_offline_mode():
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    supplied = config.attributes.get("connection")
    engine = None if supplied is not None else build_engine(database_url())
    try:
        with nullcontext(supplied) if supplied is not None else engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        if engine is not None:
            engine.dispose()
