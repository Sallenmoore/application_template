"""
# Components API Documentation

## Components Endpoints

"""

import random

from flask import Blueprint, get_template_attribute

from autonomous import log

from ._utilities import loader as _loader

index_endpoint = Blueprint("page", __name__)


###########################################################
##                    Component Routes                   ##
###########################################################
@index_endpoint.route(
    "/auth/login",
    methods=(
        "GET",
        "POST",
    ),
)
def login():
    return get_template_attribute("login.html", "login")()


@index_endpoint.route(
    "/home",
    methods=(
        "GET",
        "POST",
    ),
)
def home():
    user, *_ = _loader()
    return get_template_attribute("home.html", "home")(user)
