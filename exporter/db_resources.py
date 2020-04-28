# coding=utf-8

from sqlalchemy import Boolean, Column, String, Integer, Float, DateTime

from db_base import Session, engine, Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True)
    tag_group = Column(String)
    account_name = Column(String)
    service = Column(String)
    region = Column(String)
    availability_zone = Column(String)
    last_seen = Column(DateTime(timezone=True))
    state = Column(String)
    normalized_capacity = Column(Integer)
    image_id = Column(String)
    instance_type = Column(String)
    launch_time = Column(DateTime(timezone=True))
    private_ip_address = Column(String)
    public_ip_address = Column(String)
    state = Column(String)
    subnet_id = Column(String)
    vpc_id = Column(String)
    architecture = Column(String)
    hypervisor = Column(String)
    engine = Column(String)
    multi_az = Column(Boolean)
    allocated_storage = Column(Float)
    iops = Column(Integer)
    tags = Column(String)

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.tag_group = kwargs["tag_group"]
        self.account_name = kwargs["account_name"]
        self.service = kwargs["service"]
        self.region = kwargs["region"]
        self.availability_zone = kwargs["availability_zone"]
        self.last_seen = kwargs["last_seen"]
        self.state = kwargs["state"]
        self.instance_class = kwargs["instance_class"]
        self.normalized_capacity = kwargs["normalized_capacity"]
        self.image_id = kwargs["image_id"]
        self.instance_type = kwargs["instance_type"]
        self.launch_time = kwargs["launch_time"]
        self.private_ip_address = kwargs["private_ip_address"]
        self.public_ip_address = kwargs["public_ip_address"]
        self.state = kwargs["state"]
        self.subnet_id = kwargs["subnet_id"]
        self.vpc_id = kwargs["vpc_id"]
        self.architecture = kwargs["architecture"]
        self.hypervisor = kwargs["hypervisor"]
        self.engine = kwargs["engine"]
        self.multi_az = kwargs["multi_az"]
        self.allocated_storage = kwargs["allocated_storage"]
        self.iops = kwargs["iops"]
        self.tags = kwargs["tags"]


def upsert_resources_data(processed_tagged_resources_data):
    print("Creating database session..")
    session = Session()
    print("Creating resource objects..")
    resource_objects = {}
    for r_id in processed_tagged_resources_data:
        resource_objects[r_id] = Resource(
            **processed_tagged_resources_data[r_id]
        )
    print("Updating existing resource data..")
    for resource in (
        session.query(Resource)
        .filter(Resource.id.in_(processed_tagged_resources_data.keys()))
        .all()
    ):
        session.merge(resource_objects.pop(resource.id))
    print("Creating new resource data..")
    session.add_all(resource_objects.values())
    print("Commit and close database session..")
    session.commit()
    session.close()
