from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String)
    service_interval: Mapped[int | None] = mapped_column(Integer, nullable=True)

    cars: Mapped[list["Car"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_car_per_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="cars")
    refuelings: Mapped[list["RefuelingModel"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    maintenances: Mapped[list["MaintenanceModel"]] = relationship(back_populates="car", cascade="all, delete-orphan")


class RefuelingModel(Base):
    __tablename__ = "refuelings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime)
    odo: Mapped[int] = mapped_column(Integer)
    filing_volume: Mapped[float] = mapped_column(Float)

    car: Mapped[Car] = relationship(back_populates="refuelings")


class MaintenanceModel(Base):
    __tablename__ = "maintenances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"))
    performed_at: Mapped[dt.date] = mapped_column(Date)
    odo: Mapped[int] = mapped_column(Integer)

    car: Mapped[Car] = relationship(back_populates="maintenances")
