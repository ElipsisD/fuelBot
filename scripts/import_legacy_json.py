from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select

from app.config import load_config
from app.db.models import Car, MaintenanceModel, RefuelingModel, User
from app.db.session import get_session_factory

DEFAULT_SOURCE = load_config().db.data_dir / "db.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import legacy JSON data into the SQLite schema managed by Alembic.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Path to legacy JSON file. Default: {DEFAULT_SOURCE}",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Import even if the database already contains users.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import_legacy_json(args.source, force=args.force)


def import_legacy_json(source: Path, *, force: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Legacy JSON file not found: {source}")

    session_factory = get_session_factory()
    with session_factory() as session:
        has_users = session.scalar(select(User.telegram_id).limit(1)) is not None
        if has_users and not force:
            raise RuntimeError(
                "Database already contains users. "
                "Use --force only if you intentionally want to import into a non-empty database."
            )

        legacy_data = json.loads(source.read_text(encoding="utf-8"))
        for user_id, payload in legacy_data.items():
            user_id_str = str(user_id)
            user = User(
                telegram_id=user_id_str,
                username=payload.get("username"),
                first_name=payload.get("first_name") or "",
                service_interval=payload.get("service_interval"),
            )
            session.merge(user)
            session.flush()

            cars: dict[str, Car] = {}
            for car_name, is_deleted in _iter_legacy_cars(payload.get("cars", [])):
                car = _get_or_create_car(session, user_id_str, car_name, is_deleted=is_deleted)
                cars[car_name] = car

            for ref in payload.get("refuelings", []):
                car = cars.get(ref["car"]) or _get_or_create_car(
                    session,
                    user_id_str,
                    ref["car"],
                    is_deleted=True,
                )
                cars[car.name] = car
                session.add(
                    RefuelingModel(
                        car_id=car.id,
                        created_at=datetime.fromisoformat(ref["date"]),
                        odo=int(ref["odo"]),
                        filing_volume=float(ref["filing_volume"]),
                    )
                )

            for maintenance in payload.get("maintenances", []):
                car = cars.get(maintenance["car"]) or _get_or_create_car(
                    session,
                    user_id_str,
                    maintenance["car"],
                    is_deleted=True,
                )
                cars[car.name] = car
                session.add(
                    MaintenanceModel(
                        car_id=car.id,
                        performed_at=date.fromisoformat(maintenance["date"]),
                        odo=int(maintenance["odo"]),
                    )
                )

        session.commit()


def _iter_legacy_cars(raw_cars) -> list[tuple[str, bool]]:
    if isinstance(raw_cars, dict):
        return [(car_name, bool(is_deleted)) for car_name, is_deleted in raw_cars.items()]
    return [(car_name, False) for car_name in raw_cars]


def _get_or_create_car(session, user_id: str, car_name: str, *, is_deleted: bool) -> Car:
    car = session.scalar(
        select(Car).where(Car.user_id == user_id, Car.name == car_name)
    )
    if car is not None:
        car.is_deleted = is_deleted
        return car

    car = Car(user_id=user_id, name=car_name, is_deleted=is_deleted)
    session.add(car)
    session.flush()
    return car


if __name__ == "__main__":
    main()
