# coding=utf-8

from sqlalchemy import Boolean, Column, String, Integer, Float, Date

from db_base import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True)
    tag_group = Column(String)
    account_name = Column(String)
    service = Column(String)
    region = Column(String)
    availability_zone = Column(String)
    state = Column(String)
    normalized_capacity = Column(Integer)
    image_id = Column(String)
    instance_type = Column(String)
    launch_time = Column(Date)
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
