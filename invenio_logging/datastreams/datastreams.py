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
        app.config.setdefault("LOGGING_DATASTREAMS_INDEXES", {
            "audit": "logs-audit",
            "jobs": "logs-job",
        })
        app.config.setdefault("LOGGING_DATASTREAMS_LEVEL", logging.INFO)

    def log_event(self, log_type, action, resource_id, resource_type, user_id=None, json={}):
        """Log an event to the appropriate OpenSearch Datastream based on log_type."""

        if not self.client:
            return
        now = datetime.now().isoformat()
        message = current_app.config["LOGGING_DATASTREAMS_MESSAGES"].get(action).format(
            log_type=log_type,
            action=action,
            timestamp=now,
            resource_id=resource_id,
            resource_type=resource_type,
            user_id=user_id,
        )
        # Determine the correct index based on log_type
        search_prefix = current_app.config["SEARCH_INDEX_PREFIX"]
        index = search_prefix + self.index_mapping.get(log_type)

        # Add all the discovered fields to the log entry (IP ADDRESS,)

        log_entry = {
            "@timestamp": now,
            "action": action,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "user_id": user_id,
            "message": message,
            # "json": json,
        }

        self.client.index(index=index, body=log_entry)