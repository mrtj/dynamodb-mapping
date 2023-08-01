"""Top-level package for DynamoDB Mapping."""

from __future__ import annotations

from .dynamodb_mapping import DynamoDBMapping, DynamoDBKeySimplified, DynamoDBItemType

__author__ = """Janos Tolgyesi"""
__email__ = "janos.tolgyesi@gmail.com"
__version__ = "0.1.0"
__all__ = ["DynamoDBMapping", "DynamoDBKeySimplified", "DynamoDBItemType"]
