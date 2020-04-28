import json

from aws import AwsClient


def get_my_tagged_resources(**kwargs):
    tagged_resources = {}
    for account in kwargs["accounts"]:
        aws_client = AwsClient(kwargs["aws_region"], account)
        for enabled_service in kwargs["enabled_services"]:
            if enabled_service not in tagged_resources:
                tagged_resources[enabled_service] = {}
            if enabled_service == "ec2":
                for tag_group in kwargs["ec2_tag_groups"]:
                    if tag_group["aws_region"] == kwargs["aws_region"]:
                        if (
                            tag_group["name"]
                            not in tagged_resources[enabled_service]
                        ):
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ] = []
                        for tag in tag_group["tags"]:
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ].extend(
                                aws_client.get_my_ec2_instances(
                                    tag["tag_name"], tag["tag_value"],
                                )
                            )
            if enabled_service == "rds":
                for tag_group in kwargs["rds_tag_groups"]:
                    if tag_group["aws_region"] == kwargs["aws_region"]:
                        if (
                            tag_group["name"]
                            not in tagged_resources[enabled_service]
                        ):
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ] = []
                        for tag in tag_group["tags"]:
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ].extend(
                                aws_client.get_my_rds_instances(
                                    tag["tag_name"], tag["tag_value"],
                                )
                            )
    return tagged_resources


def get_resource_instance_class(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceType"].split(".")[0]
    elif aws_service == "rds":
        return "db.{}".format(resource["DBInstanceClass"].split(".")[1])
    else:
        raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_normalized_capacity(
    aws_service, resource, mode="single_instance"
):
    size_to_normalized = {
        "nano": 0.25,
        "micro": 0.5,
        "small": 1,
        "medium": 2,
        "large": 4,
        "xlarge": 8,
        "2xlarge": 16,
        "3xlarge": 24,
        "4xlarge": 32,
        "6xlarge": 48,
        "8xlarge": 64,
        "9xlarge": 72,
        "10xlarge": 80,
        "12xlarge": 96,
        "16xlarge": 128,
        "18xlarge": 144,
        "24xlarge": 192,
        "32xlarge": 256,
    }
    if aws_service == "ec2":
        ec2_size = resource["InstanceType"].split(".")[1]
        if ec2_size in size_to_normalized:
            if mode == "single_instance":
                return size_to_normalized[ec2_size]
            elif mode == "all_instances":
                return size_to_normalized[ec2_size] * resource["InstanceCount"]
            else:
                raise Exception("Unexpected mode {}".format(mode))
        else:
            return ""
    elif aws_service == "rds":
        rds_size = resource["DBInstanceClass"].split(".")[2]
        rds_multi_az = resource["MultiAZ"]
        rds_size_normalized = size_to_normalized[rds_size]
        if rds_multi_az:
            rds_size_normalized = rds_size_normalized * 2
        if mode == "single_instance":
            return rds_size_normalized
        elif mode == "all_instances":
            return rds_size_normalized * resource["DBInstanceCount"]
        else:
            raise Exception("Unexpected mode {}".format(mode))
    else:
        raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceId"]
    if aws_service == "rds":
        return resource["DBInstanceIdentifier"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_availability_zone(aws_service, resource):
    if aws_service == "ec2":
        return resource["Placement"]["AvailabilityZone"]
    if aws_service == "rds":
        return resource["AvailabilityZone"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_image_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["ImageId"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_instance_type(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceType"]
    if aws_service == "rds":
        return resource["DBInstanceClass"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_launch_time(aws_service, resource):
    if aws_service == "ec2":
        return resource["LaunchTime"]
    if aws_service == "rds":
        return resource["InstanceCreateTime"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_ip(aws_service, resource, type="private"):
    if aws_service == "ec2":
        if type == "private":
            return resource["PrivateIpAddress"]
        elif type == "public":
            if "PublicIpAddress" in resource:
                return resource["PublicIpAddress"]
            else:
                return None
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_state(aws_service, resource):
    if aws_service == "ec2":
        return resource["State"]["Name"]
    if aws_service == "rds":
        return resource["DBInstanceStatus"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_subnet_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["SubnetId"]
    if aws_service == "rds":
        return resource["DBSubnetGroup"]["DBSubnetGroupName"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_vpc_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["VpcId"]
    if aws_service == "rds":
        return resource["DBSubnetGroup"]["VpcId"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_architecture(aws_service, resource):
    if aws_service == "ec2":
        return resource["Architecture"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_hypervisor(aws_service, resource):
    if aws_service == "ec2":
        return resource["Hypervisor"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_engine(aws_service, resource):
    if aws_service == "ec2":
        return None
    if aws_service == "rds":
        return resource["Engine"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_multi_az(aws_service, resource):
    if aws_service == "ec2":
        return None
    if aws_service == "rds":
        return resource["MultiAZ"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_allocated_storage(aws_service, resource):
    if aws_service == "ec2":
        return 0
    if aws_service == "rds":
        return resource["AllocatedStorage"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_iops(aws_service, resource):
    if aws_service == "ec2":
        return None
    if aws_service == "rds":
        if "Iops" in resource:
            return resource["Iops"]
        else:
            return 0
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_tags(aws_service, resource):
    if aws_service == "ec2":
        return json.dumps(resource["Tags"])
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))
