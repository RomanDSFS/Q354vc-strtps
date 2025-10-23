from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context
import asyncio
import sys
import os

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))   
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sourcng_service")))  

# ✅ Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ✅ Указываем путь к sourcing_service
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sourcing_service")))

from sourcing_service.database import Base  # Теперь путь корректный
from sourcing_service import models  # ✅ Убедимся, что модели загружены

# Подключение к конфигу Alembic
config = context.config

# Логирование Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импорт моделей для автогенерации миграций
#from sourcing_service.models import Base  # Замените на путь к вашим моделям
target_metadata = Base.metadata

# Асинхронный движок
connectable = create_async_engine(
    config.get_main_option("sqlalchemy.url"),
    poolclass=pool.NullPool,
)

async def run_migrations_online():
    """Асинхронный запуск миграций."""
    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Запуск миграций в синхронном режиме (внутри асинхронного вызова)."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())
