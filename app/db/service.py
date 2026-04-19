from __future__ import annotations

import datetime as dt

from app.db.repository import DatabaseRepository, repository
from app.db.session import session_scope
from app.db.types import Maintenance, Refueling
from app.utils import exceptions, strtime
from app.utils.exceptions import NotCorrectCarName


class DatabaseService:
    def __init__(self, repo: DatabaseRepository) -> None:
        self.repo = repo

    def new_user_check(self, user_id: str) -> bool:
        with session_scope() as session:
            return self.repo.get_user(session, user_id) is None

    def set_new_user_data(self, user_id: str, username: str | None, first_name: str, car_name: str) -> None:
        with session_scope() as session:
            user = self.repo.create_user(session, user_id, username, first_name)
            self.repo.create_car(session, user.telegram_id, car_name, is_deleted=False)
            session.commit()

    def new_refueling(self, user_id: str, car: str, odo: int, filing_volume: float) -> None:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                raise NotCorrectCarName("Автомобиль не найден")
            self.repo.create_refueling(
                session,
                car_id=car_model.id,
                created_at=self._parse_datetime(strtime.get_now_formatted()),
                odo=odo,
                filing_volume=filing_volume,
            )
            session.commit()

    def user_cars(self, user_id: str) -> list[str]:
        with session_scope() as session:
            return self.repo.list_active_car_names(session, user_id)

    def get_last_odo_on_car(self, user_id: str, car: str) -> int:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                return 0
            ref = self.repo.get_last_non_zero_odo_refueling(session, car_model.id)
            return ref.odo if ref else 0

    def get_two_last_full_ref_on_car(self, user_id: str, car: str) -> list[dict]:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                return []
            refs = self.repo.list_refuelings_desc(session, car_model.id)
            result: list[dict] = []
            first_full_idx: int | None = None
            for idx, ref in enumerate(refs):
                if ref.odo != 0:
                    result.append(self._ref_to_dict(ref, car_model.name))
                    first_full_idx = idx
                    break
            if first_full_idx is None:
                return []
            for ref in refs[first_full_idx + 1:]:
                result.append(self._ref_to_dict(ref, car_model.name))
                if ref.odo != 0:
                    return result
            return []

    def get_last_user_refueling(self, user_id: str) -> Refueling | None:
        with session_scope() as session:
            row = self.repo.get_last_user_refueling_row(session, user_id)
            if row is None:
                return None
            ref, car_name = row
            return Refueling(
                date=ref.created_at.isoformat(sep=" "),
                odo=ref.odo,
                filing_volume=ref.filing_volume,
                car=car_name,
            )

    def change_last_refueling(self, user_id: str, odo: int, filing_volume: float) -> None:
        with session_scope() as session:
            ref = self.repo.get_last_user_refueling_model(session, user_id)
            if ref is None:
                return
            ref.odo = odo
            ref.filing_volume = filing_volume
            session.commit()

    def get_last_partial_ref_on_car(self, user_id: str, car: str) -> list[dict]:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                return []
            refs = self.repo.list_refuelings_desc(session, car_model.id)
            result: list[dict] = []
            for ref in refs:
                if ref.odo != 0:
                    return result
                result.append(self._ref_to_dict(ref, car_model.name))
            return result

    def add_new_car(self, user_id: str, car: str) -> None:
        with session_scope() as session:
            existing_car = self.repo.get_car(session, user_id, car)
            if existing_car is not None and not existing_car.is_deleted:
                raise NotCorrectCarName(
                    'У тебя уже есть автомобиль с таким названием!\n'
                    'Попробуй еще раз!'
                )
            if existing_car is not None:
                existing_car.is_deleted = False
            else:
                self.repo.create_car(session, user_id, car, is_deleted=False)
            session.commit()

    def delete_car(self, user_id: str, car: str) -> None:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                return
            car_model.is_deleted = True
            session.commit()

    def get_refuelings_list(self, user_id: str, car: str) -> list[Refueling]:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                return []
            return [
                Refueling(
                    date=ref.created_at.isoformat(sep=" "),
                    odo=ref.odo,
                    filing_volume=ref.filing_volume,
                    car=car_model.name,
                )
                for ref in self.repo.list_refuelings_asc(session, car_model.id)
            ]

    def get_service_interval(self, user_id: str) -> int | None:
        with session_scope() as session:
            user = self.repo.get_user(session, user_id)
            return user.service_interval if user else None

    def set_service_interval(self, user_id: str, interval: int) -> None:
        with session_scope() as session:
            user = self.repo.get_user(session, user_id)
            if user is None:
                return
            user.service_interval = interval
            session.commit()

    def new_maintenance(self, user_id: str, info: Maintenance) -> None:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, info.car)
            if car_model is None:
                raise NotCorrectCarName("Автомобиль не найден")
            self.repo.create_maintenance(
                session,
                car_id=car_model.id,
                performed_at=self._parse_date(info.date),
                odo=info.odo,
            )
            session.commit()

    def get_last_maintenance(self, user_id: str, car: str) -> Maintenance:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                raise exceptions.NotFoundMaintenance('Данные о ТО отсутствуют')
            maintenance = self.repo.get_last_maintenance_model(session, car_model.id)
            if maintenance is None:
                raise exceptions.NotFoundMaintenance('Данные о ТО отсутствуют')
            return Maintenance(maintenance.performed_at.isoformat(), car_model.name, maintenance.odo)

    def get_refuelings_list_for_month(self, user_id: str, car: str) -> list[Refueling]:
        threshold = dt.datetime.today() - dt.timedelta(days=30)
        return self._get_refuelings_since(user_id, car, threshold)

    def get_refuelings_list_for_current_year(self, user_id: str, car: str) -> list[Refueling]:
        today_year = dt.datetime.today().year
        year_start = dt.datetime(today_year, 1, 1)
        return self._get_refuelings_since(user_id, car, year_start)

    def _get_refuelings_since(self, user_id: str, car: str, threshold: dt.datetime) -> list[Refueling]:
        with session_scope() as session:
            car_model = self.repo.get_car(session, user_id, car)
            if car_model is None:
                return []
            return [
                Refueling(
                    date=ref.created_at.isoformat(sep=" "),
                    odo=ref.odo,
                    filing_volume=ref.filing_volume,
                    car=car_model.name,
                )
                for ref in self.repo.list_refuelings_since(session, car_model.id, threshold)
            ]

    @staticmethod
    def _parse_datetime(value: str) -> dt.datetime:
        return dt.datetime.fromisoformat(value)

    @staticmethod
    def _parse_date(value: str) -> dt.date:
        return dt.date.fromisoformat(value)

    @staticmethod
    def _ref_to_dict(ref, car_name: str) -> dict:
        return {
            "date": ref.created_at.isoformat(sep=" "),
            "car": car_name,
            "odo": ref.odo,
            "filing_volume": ref.filing_volume,
        }


service = DatabaseService(repository)
