from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    snils: Mapped[str] = mapped_column(String(20))
    driver_license: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    waybills: Mapped[list["Waybill"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(30))  # легковой/грузовой/спецтехника/автокран
    brand_model: Mapped[str] = mapped_column(String(100))
    vin: Mapped[str] = mapped_column(String(17))
    gov_number: Mapped[str] = mapped_column(String(20))
    odometer_start: Mapped[int] = mapped_column(Integer, default=0)

    waybills: Mapped[list["Waybill"]] = relationship(back_populates="vehicle")


class Trailer(Base):
    __tablename__ = "trailers"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_model: Mapped[str] = mapped_column(String(100))
    vin: Mapped[str] = mapped_column(String(17))
    reg_number: Mapped[str] = mapped_column(String(20))

    waybills: Mapped[list["Waybill"]] = relationship(back_populates="trailer")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(20), nullable=True)

    waybills: Mapped[list["Waybill"]] = relationship(back_populates="customer")


class Waybill(Base):
    __tablename__ = "waybills"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(30))
    date_issue: Mapped[date] = mapped_column(Date)
    date_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    route: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_type: Mapped[str] = mapped_column(String(30))

    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    trailer_id: Mapped[int | None] = mapped_column(ForeignKey("trailers.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)

    driver: Mapped["Driver"] = relationship(back_populates="waybills")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="waybills")
    trailer: Mapped["Trailer | None"] = relationship(back_populates="waybills")
    customer: Mapped["Customer | None"] = relationship(back_populates="waybills")