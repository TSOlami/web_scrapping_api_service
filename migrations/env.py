import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
from app.models import Base

# Load environment variables
load_dotenv()

# this is the Alembic Config object
config = context.config

# Set MySQL connection URL from environment variables
section = config.config_ini_section
config.set_section_option(section, "MYSQL_USER", os.getenv("MYSQL_USER"))
config.set_section_option(section, "MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD"))
config.set_section_option(section, "MYSQL_HOST", os.getenv("MYSQL_HOST", "localhost"))
config.set_section_option(section, "MYSQL_DB", os.getenv("MYSQL_DB"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

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
