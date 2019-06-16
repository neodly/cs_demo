# -*- coding: utf-8 -*-
import logging
import sys

from flask import Flask


def create_app(config_object="cs_demo.config.ProductionConfig"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    from .models import db

    db.init_app(app)
    from .api.views import api

    app.register_blueprint(api, url_prefix="/api")
    configure_logger(app)
    return app


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
