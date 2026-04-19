from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Car, MaintenanceModel, RefuelingModel, User


class DatabaseRepository:
    def get_user(self, session: Session, user_id: str) -> User | None:
        return session.get(User, user_id)

    def get_car(self, session: Session, user_id: str, car_name: str) -> Car | None:
        stmt = select(Car).where(Car.user_id == user_id, Car.name == car_name)
        return session.scalar(stmt)

    def create_user(self, session: Session, user_id: str, username: str | None, first_name: str) -> User:
        user = User(
            telegram_id=user_id,
            username=username,
            first_name=first_name,
        )
        session.add(user)
        session.flush()
        return user

    def create_car(self, session: Session, user_id: str, car_name: str, *, is_deleted: bool = False) -> Car:
        car = Car(user_id=user_id, name=car_name, is_deleted=is_deleted)
        session.add(car)
        session.flush()
        return car

    def list_active_car_names(self, session: Session, user_id: str) -> list[str]:
        stmt = (
            select(Car.name)
            .where(Car.user_id == user_id, Car.is_deleted.is_(False))
            .order_by(Car.id.asc())
        )
        return list(session.scalars(stmt))

    def create_refueling(
        self,
        session: Session,
        *,
        car_id: int,
        created_at: dt.datetime,
        odo: int,
        filing_volume: float,
    ) -> None:
        session.add(
            RefuelingModel(
                car_id=car_id,
                created_at=created_at,
                odo=odo,
                filing_volume=filing_volume,
            )
        )

    def get_last_non_zero_odo_refueling(self, session: Session, car_id: int) -> RefuelingModel | None:
        stmt = (
            select(RefuelingModel)
            .where(RefuelingModel.car_id == car_id, RefuelingModel.odo != 0)
            .order_by(RefuelingModel.created_at.desc(), RefuelingModel.id.desc())
        )
        return session.scalar(stmt)

    def list_refuelings_desc(self, session: Session, car_id: int) -> list[RefuelingModel]:
        stmt = (
            select(RefuelingModel)
            .where(RefuelingModel.car_id == car_id)
            .order_by(RefuelingModel.created_at.desc(), RefuelingModel.id.desc())
        )
        return list(session.scalars(stmt))

    def get_last_user_refueling_row(self, session: Session, user_id: str):
        stmt = (
            select(RefuelingModel, Car.name)
            .join(Car, RefuelingModel.car_id == Car.id)
            .where(Car.user_id == user_id)
            .order_by(RefuelingModel.created_at.desc(), RefuelingModel.id.desc())
        )
        return session.execute(stmt).first()

    def get_last_user_refueling_model(self, session: Session, user_id: str) -> RefuelingModel | None:
        stmt = (
            select(RefuelingModel)
            .join(Car, RefuelingModel.car_id == Car.id)
            .where(Car.user_id == user_id)
            .order_by(RefuelingModel.created_at.desc(), RefuelingModel.id.desc())
        )
        return session.scalar(stmt)

    def list_refuelings_asc(self, session: Session, car_id: int) -> list[RefuelingModel]:
        stmt = (
            select(RefuelingModel)
            .where(RefuelingModel.car_id == car_id)
            .order_by(RefuelingModel.created_at.asc(), RefuelingModel.id.asc())
        )
        return list(session.scalars(stmt))

    def list_refuelings_since(self, session: Session, car_id: int, threshold: dt.datetime) -> list[RefuelingModel]:
        stmt = (
            select(RefuelingModel)
            .where(RefuelingModel.car_id == car_id, RefuelingModel.created_at >= threshold)
            .order_by(RefuelingModel.created_at.asc(), RefuelingModel.id.asc())
        )
        return list(session.scalars(stmt))

    def create_maintenance(self, session: Session, *, car_id: int, performed_at: dt.date, odo: int) -> None:
        session.add(
            MaintenanceModel(
                car_id=car_id,
                performed_at=performed_at,
                odo=odo,
            )
        )

    def get_last_maintenance_model(self, session: Session, car_id: int) -> MaintenanceModel | None:
        stmt = (
            select(MaintenanceModel)
            .where(MaintenanceModel.car_id == car_id)
            .order_by(MaintenanceModel.performed_at.desc(), MaintenanceModel.id.desc())
        )
        return session.scalar(stmt)


repository = DatabaseRepository()
