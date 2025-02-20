# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio OpenSearch Datastream Logging module."""

from __future__ import absolute_import, print_function
import logging
from datetime import datetime
from flask import current_app
from opensearchpy import OpenSearch

from invenio_logging.ext import InvenioLoggingBase
from marshmallow import ValidationError
from .schema import LogEventSchema


class InvenioLoggingDatastreams(InvenioLoggingBase):
    """Invenio-Logging extension for OpenSearch Datastreams."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        if not app.config["LOGGING_DATASTREAMS_ENABLED"]:
            return

        self.client = OpenSearch(app.config["LOGGING_DATASTREAMS_HOST"])
        self.index_mapping = app.config["LOGGING_DATASTREAMS_INDEXES"]

        app.extensions["invenio-logging-datastreams"] = app.datastream_logger = self

    def init_config(self, app):
        """Initialize config with defaults."""
        app.config.setdefault("LOGGING_DATASTREAMS_ENABLED", True)
        app.config.setdefault("LOGGING_DATASTREAMS_HOST", "http://localhost:9200")
        app.config.setdefault(
            "LOGGING_DATASTREAMS_INDEXES",
            {
                "audit": "logs-audit",
                "job": "logs-job",
            },
        )
        app.config.setdefault("LOGGING_DATASTREAMS_LEVEL", logging.INFO)

    def log_event(self, log_type, log_data):
        """Log an event to OpenSearch with minimal processing, assuming pre-formatted log_data."""

        if not self.client:
            return

        try:
            # Ensure timestamp is present and in UTC format
            if "timestamp" not in log_data:
                log_data["timestamp"] = datetime.now()

            action = log_data.get("event", {}).get("action")
            # Fetch message template from config
            message_template = (current_app.config["LOGGING_DATASTREAMS_MESSAGES"]
                .get(action, f"{action} event occurred")
                .format(**log_data, **log_data.get("process", {}), **log_data.get("user", {}))
            )
            message = (
                message_template.format(**log_data)
                if message_template
                else f"{log_data.get('action')} event occurred"
            )
            log_data["message"] = message

            # Validate log data using the Marshmallow schema
            validated_log = LogEventSchema().dump(log_data)

            # Determine the correct index based on log_type
            search_prefix = current_app.config["SEARCH_INDEX_PREFIX"]
            index = search_prefix + self.index_mapping.get(log_type)
            import pdb

            pdb.set_trace()
            # Send the validated log to OpenSearch
            self.client.index(index=index, body=validated_log)

        except ValidationError as e:
            print(f"Invalid log data: {e.messages}")
        except Exception as e:
            print(f"Error logging event: {e}")
