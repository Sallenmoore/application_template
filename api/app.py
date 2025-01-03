import os

from config import Config
from flask import Flask, url_for
from views import index,  nav

from autonomous import log
from autonomous.auth import AutoAuth
from models.user import User


def create_app():
    app = Flask(os.getenv("APP_NAME", __name__))
    app.config.from_object(Config)

    #################################################################
    #                                                        Plug-ins                                      #
    #################################################################

    AutoAuth.user_class = User
    # Configure Filters
    if app.config["DEBUG"]:
        app.jinja_env.add_extension("jinja2.ext.debug")

    ######################################
    #              Routes                #
    ######################################
    @app.route("/favicon.ico")
    def favicon():
        return url_for("static", filename="images/favicon.ico")

    ######################################
    #           Blueprints               #
    ######################################
    app.register_blueprint(nav.nav_endpoint, url_prefix="/nav")
    app.register_blueprint(index.index_endpoint, url_prefix="/")
    return app
