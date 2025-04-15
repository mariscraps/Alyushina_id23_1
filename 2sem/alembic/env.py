from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool  # для создания подключения к БД
from alembic import context  # основной объект Alembic для управления миграциями
import os  # для работы с путями
import sys
from dotenv import load_dotenv

# добавляем родительскую директорию в sys.path, чтобы python мог находить
# модули проекта (например, app.db.base)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# загружает переменные окружения из файла .env
load_dotenv()

from app.db.base import Base
from app.models.user import User

config = context.config  # загружаем конфигурацию Alembic из alembic.ini
fileConfig(config.config_file_name)  # настраиваем логгирование на основе alembic.ini
target_metadata = Base.metadata  # указываем Alembic, какие таблицы нужно мигрировать


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # экранируем параметры запросов
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
