"""Scaffold layer: KMS key and S3 bucket for Terraform state storage.

Mirrors the resources from 01-scaffold/ in the Terraform project.
"""

from dataclasses import dataclass

import pulumi
import pulumi_aws as aws


@dataclass
class ScaffoldOutputs:
    """Outputs from the scaffold layer."""

    kms_key_arn: pulumi.Output[str]
    s3_bucket_name: pulumi.Output[str]


def create_scaffold(name_prefix: str, tags: dict[str, str]) -> ScaffoldOutputs:
    """Create the scaffold layer resources.

    Args:
        name_prefix: Prefix for naming resources.
        tags: Tags to apply to all resources.
    """
    # KMS key for encrypting S3 bucket.
    kms_key = aws.kms.Key(
        "terraform-state-key",
        description="KMS key for encrypting Terraform state in S3 and DynamoDB",
        enable_key_rotation=True,
        deletion_window_in_days=30,
        tags={**tags, "Name": f"{name_prefix}-tf-key"},
    )

    # KMS alias for the key.
    aws.kms.Alias(
        "terraform-state-key-alias",
        name=f"alias/{name_prefix}-tf-key-alias",
        target_key_id=kms_key.key_id,
    )

    # S3 bucket for storing Terraform state.
    bucket = aws.s3.BucketV2(
        "terraform-state-bucket",
        tags={**tags, "Name": f"{name_prefix}-tf-state-bucket"},
    )

    # Enable versioning on the state bucket.
    aws.s3.BucketVersioningV2(
        "terraform-state-versioning",
        bucket=bucket.id,
        versioning_configuration={
            "status": "Enabled",
        },
    )

    # Enable server-side encryption with the KMS key.
    aws.s3.BucketServerSideEncryptionConfigurationV2(
        "terraform-state-encryption",
        bucket=bucket.id,
        rules=[
            {
                "apply_server_side_encryption_by_default": {
                    "sse_algorithm": "aws:kms",
                    "kms_master_key_id": kms_key.arn,
                },
            }
        ],
    )

    # Block all public access to the state bucket.
    aws.s3.BucketPublicAccessBlock(
        "terraform-state-public-access-block",
        bucket=bucket.id,
        block_public_acls=True,
        block_public_policy=True,
        ignore_public_acls=True,
        restrict_public_buckets=True,
    )

    return ScaffoldOutputs(
        kms_key_arn=kms_key.arn,
        s3_bucket_name=bucket.bucket,
    )
