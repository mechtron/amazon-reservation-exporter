# coding=utf-8

from datetime import date

from db_actor import Actor
from db_base import Session, engine, Base
from db_contact_details import ContactDetails
from db_movie import Movie
from db_stuntman import Stuntman
from db_reservations import Reservation


def test_data_insert():
    # Generate database schema
    Base.metadata.create_all(engine)

    # Create a new session
    session = Session()

    # Create movies
    bourne_identity = Movie("The Bourne Identity", date(2002, 10, 11))
    furious_7 = Movie("Furious 7", date(2015, 4, 2))
    pain_and_gain = Movie("Pain & Gain", date(2013, 8, 23))

    # Creates actors
    matt_damon = Actor("Matt Damon", date(1970, 10, 8))
    dwayne_johnson = Actor("Dwayne Johnson", date(1972, 5, 2))
    mark_wahlberg = Actor("Mark Wahlberg", date(1971, 6, 5))

    # Add actors to movies
    bourne_identity.actors = [matt_damon]
    furious_7.actors = [dwayne_johnson]
    pain_and_gain.actors = [dwayne_johnson, mark_wahlberg]

    # Add contact details to actors
    matt_contact = ContactDetails("415 555 2671", "Burbank, CA", matt_damon)
    dwayne_contact = ContactDetails("423 555 5623", "Glendale, CA", dwayne_johnson)
    dwayne_contact_2 = ContactDetails("421 444 2323", "West Hollywood, CA", dwayne_johnson)
    mark_contact = ContactDetails("421 333 9428", "Glendale, CA", mark_wahlberg)

    # Create stuntmen
    matt_stuntman = Stuntman("John Doe", True, matt_damon)
    dwayne_stuntman = Stuntman("John Roe", True, dwayne_johnson)
    mark_stuntman = Stuntman("Richard Roe", True, mark_wahlberg)

    # Persist data
    session.add(bourne_identity)
    session.add(furious_7)
    session.add(pain_and_gain)

    session.add(matt_contact)
    session.add(dwayne_contact)
    session.add(dwayne_contact_2)
    session.add(mark_contact)

    session.add(matt_stuntman)
    session.add(dwayne_stuntman)
    session.add(mark_stuntman)

    # Commit and close session
    session.commit()
    session.close()


def upsert_reservation_data(processed_reservation_data):
    print("Generating database schema..")
    Base.metadata.create_all(engine)
    print("Creating database session..")
    session = Session()
    print("Creating and persisting reservation data..")
    for res_id in processed_reservation_data:
        processed_reservation_data[res_id]["id"] = res_id
        reservation = Reservation(
            id=processed_reservation_data[res_id]["id"],
            service=processed_reservation_data[res_id]["service"],
            state=processed_reservation_data[res_id]["state"],
            region=processed_reservation_data[res_id]["region"],
            availability_zone=processed_reservation_data[res_id]["availability_zone"],
            scope=processed_reservation_data[res_id]["scope"],
            account_name=processed_reservation_data[res_id]["account_name"],
            count=processed_reservation_data[res_id]["count"],
            instance_class=processed_reservation_data[res_id]["instance_class"],
            normalized_capacity_each=processed_reservation_data[res_id]["normalized_capacity_each"],
            normalized_capacity_total=processed_reservation_data[res_id]["normalized_capacity_total"],
            type=processed_reservation_data[res_id]["type"],
            description=processed_reservation_data[res_id]["description"],
            multi_az=processed_reservation_data[res_id]["multi_az"],
            duration=processed_reservation_data[res_id]["duration"],
            start=processed_reservation_data[res_id]["start"],
            end=processed_reservation_data[res_id]["end"],
            fixed_price=processed_reservation_data[res_id]["fixed_price"],
            usage_price=processed_reservation_data[res_id]["usage_price"],
            recurring_charges=processed_reservation_data[res_id]["recurring_charges"],
            offering_class=processed_reservation_data[res_id]["offering_class"],
            offering_type=processed_reservation_data[res_id]["offering_type"],
        )
        # reservation = Reservation(processed_reservation_data[res_id])
        session.add(reservation)
    print("Commit and close database session..")
    session.commit()
    session.close()
    print("Reservation data successfully updated.")


def get_reservation_data():
    print("Creating database session..")
    session = Session()
    print("Looking up reservation data..")
    reservation_data = session.query(Reservation).all()
    print("Reservation data successfully retrieved.")
    return reservation_data
