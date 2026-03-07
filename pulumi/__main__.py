"""Pulumi migration of Layered Terraform Practice Example.

This program composes the scaffold and foundation layers, mirroring the
layered Terraform structure in 01-scaffold/ and 02-foundation/aws/.
"""

import pulumi

from foundation import create_foundation
from scaffold import create_scaffold

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
config = pulumi.Config()
name_prefix = config.get("namePrefix") or "vishybear"
environment = config.get("environment") or "dev"
vpc_cidr = config.get("vpcCidr") or "10.0.0.0/16"
availability_zones = config.get_object("availabilityZones") or [
    "eu-west-2a",
    "eu-west-2b",
]
tags: dict[str, str] = config.get_object("tags") or {}

# ---------------------------------------------------------------------------
# Scaffold Layer (KMS + S3 state bucket)
# ---------------------------------------------------------------------------
scaffold = create_scaffold(name_prefix=name_prefix, tags=tags)

# ---------------------------------------------------------------------------
# Foundation Layer (VPC, subnets, gateways, security groups)
# ---------------------------------------------------------------------------
assert isinstance(availability_zones, list)
foundation = create_foundation(
    environment=environment,
    vpc_cidr=vpc_cidr,
    availability_zones=availability_zones,
)

# ---------------------------------------------------------------------------
# Stack Outputs
# ---------------------------------------------------------------------------

# Scaffold outputs.
pulumi.export("kms_key_arn", scaffold.kms_key_arn)
pulumi.export("s3_bucket_name", scaffold.s3_bucket_name)

# Foundation outputs.
pulumi.export("vpc_id", foundation.vpc_id)
pulumi.export("vpc_cidr", foundation.vpc_cidr)
pulumi.export("public_subnet_ids", foundation.public_subnet_ids)
pulumi.export("private_subnet_ids", foundation.private_subnet_ids)
pulumi.export("db_subnet_group_name", foundation.db_subnet_group_name)
pulumi.export("database_security_group_id", foundation.database_security_group_id)
pulumi.export(
    "application_security_group_id", foundation.application_security_group_id
)
pulumi.export("nat_gateway_ips", foundation.nat_gateway_ips)
