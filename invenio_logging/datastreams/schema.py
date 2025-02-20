# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio OpenSearch Datastream Schema."""

from marshmallow import Schema, fields, EXCLUDE, validate


class BaseProcessSchema(Schema):
    entity_id = fields.Str(
        required=True, description="Unique identifier for the process."
    )
    name = fields.Str(required=True, description="Name of the process being logged.")
    start = fields.DateTime(required=False, description="Start time of the process.")
    end = fields.DateTime(required=False, description="End time of the process.")
    exit_code = fields.Int(
        required=False, description="Exit code of the process, if applicable."
    )


class ProcessSchema(BaseProcessSchema):
    parent = fields.Nested(
        BaseProcessSchema,
        required=False,
        description="Parent process information, if applicable.",
    )


class UserSchema(Schema):
    id = fields.Str(
        required=False, description="Identifier of the user associated with the event."
    )
    name = fields.Str(
        required=False, description="Name of the user associated with the event."
    )


class EventSchema(Schema):
    action = fields.Str(required=True, description="The action that took place.")
    category = fields.Str(
        required=False,
        description="High-level categorization of the event.",
        validate=validate.OneOf(
            [
                "api",
                "authentication",
                "configuration",
                "database",
                "driver",
                "email",
                "file",
                "host",
                "iam",
                "intrusion_detection",
                "library",
                "malware",
                "network",
                "package",
                "process",
                "registry",
                "session",
                "threat",
                "vulnerability",
                "web",
            ]
        ),
    )
    type = fields.Str(
        required=False,
        description="Controlled event type values",
        validate=validate.OneOf(
            [
                "access",
                "admin",
                "allowed",
                "change",
                "connection",
                "creation",
                "deletion",
                "denied",
                "end",
                "error",
                "group",
                "indicator",
                "info",
                "installation",
                "protocol",
                "start",
                "user",
            ]
        ),
    )


class LogEventSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Prevents unknown fields from being passed

    timestamp = fields.DateTime(
        required=True,
        data_key="@timestamp",
        description="Timestamp when the event occurred.",
    )
    event = fields.Nested(EventSchema, required=True)
    message = fields.Str(
        required=True, description="Detailed description of the logged event."
    )
    user = fields.Nested(
        UserSchema,
        required=False,
        description="Information about the user related to this event.",
    )
    process = fields.Nested(
        ProcessSchema,
        required=True,
        description="Details about the process related to the event.",
    )
    json = fields.Dict(
        required=False,
        description="Additional metadata or structured data related to the event.",
    )
