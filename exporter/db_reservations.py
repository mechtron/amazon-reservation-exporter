# coding=utf-8
import datetime

from sqlalchemy import Boolean, Column, String, Integer, Float, DateTime

from db_base import Session, engine, Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True)
    service = Column(String)
    state = Column(String)
    region = Column(String)
    availability_zone = Column(String)
    scope = Column(String)
    account_name = Column(String)
    count = Column(Integer)
    instance_class = Column(String)
    normalized_capacity_each = Column(Integer)
    normalized_capacity_total = Column(Integer)
    type = Column(String)
    description = Column(String)
    multi_az = Column(Boolean)
    duration = Column(Integer)
    start = Column(DateTime(timezone=True))
    end = Column(DateTime(timezone=True))
    fixed_price = Column(Float)
    usage_price = Column(Float)
    recurring_charges = Column(Float)
    offering_class = Column(String)
    offering_type = Column(String)

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.service = kwargs["service"]
        self.state = kwargs["state"]
        self.region = kwargs["region"]
        self.availability_zone = kwargs["availability_zone"]
        self.scope = kwargs["scope"]
        self.account_name = kwargs["account_name"]
        self.count = kwargs["count"]
        self.instance_class = kwargs["instance_class"]
        self.normalized_capacity_each = kwargs["normalized_capacity_each"]
        self.normalized_capacity_total = kwargs["normalized_capacity_total"]
        self.type = kwargs["type"]
        self.description = kwargs["description"]
        self.multi_az = kwargs["multi_az"]
        self.duration = kwargs["duration"]
        self.start = kwargs["start"]
        self.end = kwargs["end"]
        self.fixed_price = kwargs["fixed_price"]
        self.usage_price = kwargs["usage_price"]
        self.recurring_charges = kwargs["recurring_charges"]
        self.offering_class = kwargs["offering_class"]
        self.offering_type = kwargs["offering_type"]


def upsert_reservation_data(processed_reservation_data):
    print("Creating database session..")
    session = Session()
    print("Creating database objects..")
    reservation_objects = {}
    for ri_id in processed_reservation_data:
        reservation_objects[ri_id] = Reservation(**processed_reservation_data[ri_id])
    print("Updating existing reservation data..")
    for reservation in session.query(Reservation).filter(
        Reservation.id.in_(processed_reservation_data.keys())
    ).all():
        session.merge(reservation_objects.pop(reservation.id))
    print("Creating new reservation data..")
    session.add_all(reservation_objects.values())
    print("Commit and close database session..")
    session.commit()
    session.close()


def get_reservation_data():
    print("Creating database session..")
    session = Session()
    print("Looking up reservation data..")
    reservation_data = session.query(Reservation).all()
    session.close()
    print("Reservation data successfully retrieved.")
    return reservation_data
