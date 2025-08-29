import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.user import Base as UserBase
from models.question import Base as QuestionBase
from models.answer import Base as AnswerBase

# Combine all metadata
from sqlalchemy import MetaData
target_metadata = MetaData()
for table in UserBase.metadata.tables.values():
    table.tometadata(target_metadata)
for table in QuestionBase.metadata.tables.values():
    table.tometadata(target_metadata)
for table in AnswerBase.metadata.tables.values():
    table.tometadata(target_metadata)

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "postgresql+psycopg2://admin:admin123@localhost:5432/syriagpt"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata is already defined above


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()