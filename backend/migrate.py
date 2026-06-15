"""轻量迁移：为已有 SQLite 库补齐 v2 字段、新表与唯一索引。"""

from sqlalchemy import inspect, text
from database import engine, Base
import models


def run_migrations():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)

    if "exchanges" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("exchanges")}
        if "flow_status" not in cols:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE exchanges ADD COLUMN flow_status VARCHAR(20) NOT NULL DEFAULT '洽谈中'"
                    )
                )

    if "market_prices" in inspector.get_table_names():
        idx_names = {idx["name"] for idx in inspector.get_indexes("market_prices")}
        uq_name = "uq_market_style_platform_date"
        if uq_name not in idx_names:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        f"CREATE UNIQUE INDEX IF NOT EXISTS {uq_name} "
                        "ON market_prices(style_id, platform, record_date) "
                        "WHERE deleted_at IS NULL"
                    )
                )
