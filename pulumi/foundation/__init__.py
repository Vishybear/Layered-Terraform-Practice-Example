"""Foundation layer: VPC, subnets, gateways, and route tables.

Mirrors the resources from 02-foundation/aws/ in the Terraform project.
"""

from dataclasses import dataclass

import pulumi
import pulumi_aws as aws


@dataclass
class FoundationOutputs:
    """Outputs from the foundation layer."""

    vpc_id: pulumi.Output[str]
    vpc_cidr: pulumi.Output[str]
    public_subnet_ids: list[pulumi.Output[str]]
    private_subnet_ids: list[pulumi.Output[str]]
    db_subnet_group_name: pulumi.Output[str]
    database_security_group_id: pulumi.Output[str]
    application_security_group_id: pulumi.Output[str]
    nat_gateway_ips: list[pulumi.Output[str]]


def create_foundation(
    environment: str,
    vpc_cidr: str,
    availability_zones: list[str],
) -> FoundationOutputs:
    """Create the foundation layer resources.

    Args:
        environment: Environment name (e.g., dev, staging, prod).
        vpc_cidr: CIDR block for the VPC.
        availability_zones: List of availability zones for subnets.
    """
    # ----------------------------------------------------------------
    # VPC
    # ----------------------------------------------------------------
    vpc = aws.ec2.Vpc(
        f"{environment}-vpc",
        cidr_block=vpc_cidr,
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={
            "Name": f"{environment}-vpc",
            "Environment": environment,
            "ManagedBy": "Pulumi",
        },
    )

    # ----------------------------------------------------------------
    # Internet Gateway
    # ----------------------------------------------------------------
    igw = aws.ec2.InternetGateway(
        f"{environment}-igw",
        vpc_id=vpc.id,
        tags={
            "Name": f"{environment}-igw",
            "Environment": environment,
        },
    )

    # ----------------------------------------------------------------
    # Public Subnets
    # ----------------------------------------------------------------
    public_subnets: list[aws.ec2.Subnet] = []
    for i, az in enumerate(availability_zones):
        subnet = aws.ec2.Subnet(
            f"{environment}-public-{az}",
            vpc_id=vpc.id,
            cidr_block=_cidr_subnet(vpc_cidr, 8, i),
            availability_zone=az,
            map_public_ip_on_launch=True,
            tags={
                "Name": f"{environment}-public-{az}",
                "Environment": environment,
                "Type": "public",
            },
        )
        public_subnets.append(subnet)

    # ----------------------------------------------------------------
    # Private Subnets
    # ----------------------------------------------------------------
    private_subnets: list[aws.ec2.Subnet] = []
    for i, az in enumerate(availability_zones):
        subnet = aws.ec2.Subnet(
            f"{environment}-private-{az}",
            vpc_id=vpc.id,
            cidr_block=_cidr_subnet(vpc_cidr, 8, i + 100),
            availability_zone=az,
            tags={
                "Name": f"{environment}-private-{az}",
                "Environment": environment,
                "Type": "private",
            },
        )
        private_subnets.append(subnet)

    # ----------------------------------------------------------------
    # Elastic IPs for NAT Gateways
    # ----------------------------------------------------------------
    eips: list[aws.ec2.Eip] = []
    for i, _az in enumerate(availability_zones):
        eip = aws.ec2.Eip(
            f"{environment}-nat-eip-{i + 1}",
            domain="vpc",
            tags={
                "Name": f"{environment}-nat-eip-{i + 1}",
                "Environment": environment,
            },
            opts=pulumi.ResourceOptions(depends_on=[igw]),
        )
        eips.append(eip)

    # ----------------------------------------------------------------
    # NAT Gateways (one per AZ, placed in public subnets)
    # ----------------------------------------------------------------
    nat_gateways: list[aws.ec2.NatGateway] = []
    for i, _az in enumerate(availability_zones):
        nat_gw = aws.ec2.NatGateway(
            f"{environment}-nat-{i + 1}",
            allocation_id=eips[i].id,
            subnet_id=public_subnets[i].id,
            tags={
                "Name": f"{environment}-nat-{i + 1}",
                "Environment": environment,
            },
        )
        nat_gateways.append(nat_gw)

    # ----------------------------------------------------------------
    # Public Route Table
    # ----------------------------------------------------------------
    public_rt = aws.ec2.RouteTable(
        f"{environment}-public-rt",
        vpc_id=vpc.id,
        routes=[
            {
                "cidr_block": "0.0.0.0/0",
                "gateway_id": igw.id,
            }
        ],
        tags={
            "Name": f"{environment}-public-rt",
            "Environment": environment,
        },
    )

    for i, pub_subnet in enumerate(public_subnets):
        aws.ec2.RouteTableAssociation(
            f"{environment}-public-rta-{i}",
            subnet_id=pub_subnet.id,
            route_table_id=public_rt.id,
        )

    # ----------------------------------------------------------------
    # Private Route Tables (one per AZ, each routing through its NAT GW)
    # ----------------------------------------------------------------
    for i, priv_subnet in enumerate(private_subnets):
        private_rt = aws.ec2.RouteTable(
            f"{environment}-private-rt-{i + 1}",
            vpc_id=vpc.id,
            routes=[
                {
                    "cidr_block": "0.0.0.0/0",
                    "nat_gateway_id": nat_gateways[i].id,
                }
            ],
            tags={
                "Name": f"{environment}-private-rt-{i + 1}",
                "Environment": environment,
            },
        )

        aws.ec2.RouteTableAssociation(
            f"{environment}-private-rta-{i}",
            subnet_id=priv_subnet.id,
            route_table_id=private_rt.id,
        )

    # ----------------------------------------------------------------
    # DB Subnet Group (for RDS databases)
    # ----------------------------------------------------------------
    db_subnet_group = aws.rds.SubnetGroup(
        f"{environment}-db-subnet-group",
        subnet_ids=[s.id for s in private_subnets],
        tags={
            "Name": f"{environment}-db-subnet-group",
            "Environment": environment,
        },
    )

    # ----------------------------------------------------------------
    # Security Group: Database
    # ----------------------------------------------------------------
    database_sg = aws.ec2.SecurityGroup(
        f"{environment}-database-sg",
        description="Security group for database instances",
        vpc_id=vpc.id,
        ingress=[
            {
                "description": "PostgreSQL from VPC",
                "from_port": 5432,
                "to_port": 5432,
                "protocol": "tcp",
                "cidr_blocks": [vpc_cidr],
            },
            {
                "description": "MySQL from VPC",
                "from_port": 3306,
                "to_port": 3306,
                "protocol": "tcp",
                "cidr_blocks": [vpc_cidr],
            },
        ],
        egress=[
            {
                "description": "Allow all outbound",
                "from_port": 0,
                "to_port": 0,
                "protocol": "-1",
                "cidr_blocks": ["0.0.0.0/0"],
            },
        ],
        tags={
            "Name": f"{environment}-database-sg",
            "Environment": environment,
        },
    )

    # ----------------------------------------------------------------
    # Security Group: Application
    # ----------------------------------------------------------------
    application_sg = aws.ec2.SecurityGroup(
        f"{environment}-application-sg",
        description="Security group for application servers",
        vpc_id=vpc.id,
        ingress=[
            {
                "description": "HTTP from anywhere",
                "from_port": 80,
                "to_port": 80,
                "protocol": "tcp",
                "cidr_blocks": ["0.0.0.0/0"],
            },
            {
                "description": "HTTPS from anywhere",
                "from_port": 443,
                "to_port": 443,
                "protocol": "tcp",
                "cidr_blocks": ["0.0.0.0/0"],
            },
            {
                "description": "SSH from VPC",
                "from_port": 22,
                "to_port": 22,
                "protocol": "tcp",
                "cidr_blocks": [vpc_cidr],
            },
        ],
        egress=[
            {
                "description": "Allow all outbound",
                "from_port": 0,
                "to_port": 0,
                "protocol": "-1",
                "cidr_blocks": ["0.0.0.0/0"],
            },
        ],
        tags={
            "Name": f"{environment}-application-sg",
            "Environment": environment,
        },
    )

    return FoundationOutputs(
        vpc_id=vpc.id,
        vpc_cidr=vpc.cidr_block,
        public_subnet_ids=[s.id for s in public_subnets],
        private_subnet_ids=[s.id for s in private_subnets],
        db_subnet_group_name=db_subnet_group.name,
        database_security_group_id=database_sg.id,
        application_security_group_id=application_sg.id,
        nat_gateway_ips=[eip.public_ip for eip in eips],
    )


def _cidr_subnet(base_cidr: str, new_bits: int, net_num: int) -> str:
    """Compute a subnet CIDR, equivalent to Terraform's cidrsubnet().

    For a /16 base with new_bits=8, this produces /24 subnets.
    """
    import ipaddress

    network = ipaddress.ip_network(base_cidr, strict=False)
    new_prefix = network.prefixlen + new_bits
    subnets = list(network.subnets(new_prefix=new_prefix))
    return str(subnets[net_num])
