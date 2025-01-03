"""
# Components API Documentation

## Components Endpoints

"""

import os
import random

import requests
from flask import Blueprint, get_template_attribute, request
from jinja2 import TemplateNotFound

from autonomous import log
from models.campaign.campaign import Campaign
from models.world import World

from ._utilities import loader as _loader
from .campaign import index as campaign_endpoint

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
    worlds = World.all()
    worlds = random.sample(worlds, 4) if len(worlds) > 4 else worlds
    return get_template_attribute("login.html", "login")(worlds=worlds)


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


