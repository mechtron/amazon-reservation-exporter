#!/usr/bin/env python3

import datetime
from pathlib import Path

import pytz
import yaml


from aws_reservations import (
    get_my_reservations,
    get_reservation_id,
    get_reservation_az,
    get_reservation_scope,
    get_reservation_instance_count,
    get_reservation_type,
    get_reservation_multi_az,
    get_reservation_start_date,
    get_reservation_end_date,
    get_reservation_recurring_charges,
    get_reservation_offering_class,
)
from aws_resources import (
    get_my_tagged_resources,
    get_resource_instance_class,
    get_resource_normalized_capacity,
    get_resource_id,
    get_resource_availability_zone,
    get_resource_image_id,
    get_resource_instance_type,
    get_resource_launch_time,
    get_resource_ip,
    get_resource_state,
    get_resource_subnet_id,
    get_resource_vpc_id,
    get_resource_architecture,
    get_resource_hypervisor,
    get_resource_engine,
    get_resource_multi_az,
    get_resource_allocated_storage,
    get_resource_iops,
    get_resource_tags,
)
from db_base import generate_database_schema
from db_reservations import upsert_reservation_data
from db_resources import upsert_resources_data


def process_aws_reservation_data(reservation_data):
    first_region = list(reservation_data.keys())[0]
    services_enabled = list(reservation_data[first_region].keys())
    reservations = {}
    for aws_service in services_enabled:
        for aws_region in reservation_data:
            print(
                "Processing data for {aws_region} {aws_service}..".format(
                    aws_region=aws_region, aws_service=aws_service,
                )
            )
            for aws_data in reservation_data[aws_region][aws_service]:
                reservation_id = get_reservation_id(aws_service, aws_data)
                availability_zone = get_reservation_az(aws_service, aws_data,)
                scope = get_reservation_scope(aws_service, aws_data)
                instance_count = get_reservation_instance_count(
                    aws_service, aws_data,
                )
                instance_class = get_resource_instance_class(
                    aws_service, aws_data,
                )
                res_type = get_reservation_type(aws_service, aws_data)
                multi_az = get_reservation_multi_az(aws_service, aws_data)
                start = get_reservation_start_date(aws_service, aws_data)
                end = get_reservation_end_date(aws_service, aws_data)
                normalized_capacity_each = get_resource_normalized_capacity(
                    aws_service, aws_data,
                )
                normalized_capacity_total = get_resource_normalized_capacity(
                    aws_service, aws_data, "all_instances",
                )
                recurring_charges = get_reservation_recurring_charges(aws_data)
                offering_class = get_reservation_offering_class(
                    aws_service, aws_data,
                )
                reservations[reservation_id] = dict(
                    id=reservation_id,
                    service=aws_service,
                    state=aws_data["State"],
                    region=aws_region,
                    availability_zone=availability_zone,
                    scope=scope,
                    account_name=aws_data["AccountName"],
                    count=instance_count,
                    instance_class=instance_class,
                    normalized_capacity_each=normalized_capacity_each,
                    normalized_capacity_total=normalized_capacity_total,
                    type=res_type,
                    description=aws_data["ProductDescription"],
                    multi_az=multi_az,
                    duration=aws_data["Duration"],
                    start=start,
                    end=end,
                    fixed_price=aws_data["FixedPrice"],
                    usage_price=aws_data["UsagePrice"],
                    recurring_charges=recurring_charges,
                    offering_class=offering_class,
                    offering_type=aws_data["OfferingType"],
                )

    return reservations


def process_aws_tagged_resources(tagged_resources):
    first_region = list(tagged_resources.keys())[0]
    services_enabled = list(tagged_resources[first_region].keys())
    resources = {}
    for aws_service in services_enabled:
        for aws_region in tagged_resources:
            print(
                "Processing data for {aws_region} {aws_service}..".format(
                    aws_region=aws_region, aws_service=aws_service,
                )
            )
            for tag_group_name in tagged_resources[aws_region][aws_service]:
                if (
                    len(
                        tagged_resources[aws_region][aws_service][
                            tag_group_name
                        ]
                    )
                    > 0
                ):
                    for resource in tagged_resources[aws_region][aws_service][
                        tag_group_name
                    ]:
                        resource_id = get_resource_id(aws_service, resource)
                        availability_zone = get_resource_availability_zone(
                            aws_service, resource,
                        )
                        last_seen = datetime.datetime.utcnow().replace(
                            tzinfo=pytz.utc,
                        )
                        instance_class = get_resource_instance_class(
                            aws_service, resource,
                        )
                        image_id = get_resource_image_id(
                            aws_service, resource,
                        )
                        instance_type = get_resource_instance_type(
                            aws_service, resource,
                        )
                        normalized_capacity = get_resource_normalized_capacity(
                            aws_service, resource,
                        )
                        launch_time = get_resource_launch_time(
                            aws_service, resource,
                        )
                        private_ip_address = get_resource_ip(
                            aws_service, resource, "private",
                        )
                        public_ip_address = get_resource_ip(
                            aws_service, resource, "public",
                        )
                        state = get_resource_state(aws_service, resource)
                        subnet_id = get_resource_subnet_id(
                            aws_service, resource,
                        )
                        vpc_id = get_resource_vpc_id(aws_service, resource)
                        architecture = get_resource_architecture(
                            aws_service, resource,
                        )
                        hypervisor = get_resource_hypervisor(
                            aws_service, resource,
                        )
                        engine = get_resource_engine(aws_service, resource)
                        multi_az = get_resource_multi_az(aws_service, resource)
                        allocated_storage = get_resource_allocated_storage(
                            aws_service, resource,
                        )
                        iops = get_resource_iops(aws_service, resource)
                        tags = get_resource_tags(aws_service, resource)
                        resources[resource_id] = dict(
                            id=resource_id,
                            tag_group=tag_group_name,
                            account_name=resource["AccountName"],
                            service=aws_service,
                            region=aws_region,
                            availability_zone=availability_zone,
                            last_seen=last_seen,
                            instance_class=instance_class,
                            normalized_capacity=normalized_capacity,
                            image_id=image_id,
                            instance_type=instance_type,
                            launch_time=launch_time,
                            private_ip_address=private_ip_address,
                            public_ip_address=public_ip_address,
                            state=state,
                            subnet_id=subnet_id,
                            vpc_id=vpc_id,
                            architecture=architecture,
                            hypervisor=hypervisor,
                            engine=engine,
                            multi_az=multi_az,
                            allocated_storage=allocated_storage,
                            iops=iops,
                            tags=tags,
                        )
    return resources


def load_config():
    config_path = "{}/config.yml".format(Path(__file__).parent.absolute())
    with open(config_path, "r") as stream:
        return yaml.safe_load(stream)


def main():
    config = load_config()

    generate_database_schema()

    # Look-up per-service usage
    tagged_resources = {}
    for aws_region in config["aws"]["regions"]:
        tagged_resources[aws_region] = get_my_tagged_resources(
            aws_region=aws_region,
            accounts=config["aws"]["accounts"],
            enabled_services=config["aws"]["enabled_reports"],
            ec2_tag_groups=config["aws"]["ec2_tag_groups"],
            rds_tag_groups=config["aws"]["rds_tag_groups"],
        )

    # Get reservation data for all enabled regions
    reservation_data = {}
    for aws_region in config["aws"]["regions"]:
        reservation_data[aws_region] = get_my_reservations(
            aws_region,
            config["aws"]["accounts"],
            config["aws"]["enabled_reports"],
        )

    # Process data
    processed_tagged_resources_data = process_aws_tagged_resources(
        tagged_resources
    )
    processed_reservation_data = process_aws_reservation_data(reservation_data)

    # Persist reservation data to Postgres
    upsert_resources_data(processed_tagged_resources_data)
    upsert_reservation_data(processed_reservation_data)


def handler(event, context):
    main()


if __name__ == "__main__":
    main()
