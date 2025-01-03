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


def get_template(obj, macro, module=None):
    module = module or f"models/_{obj.__class__.__name__.lower()}.html"
    # log(f"Module: {module}, Macro: {macro}")
    try:
        template = get_template_attribute(module, macro)
    except (TemplateNotFound, AttributeError) as e:
        # log(e)
        module = f"shared/_{macro}.html"
        template = get_template_attribute(module, macro)
    return template


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


@index_endpoint.route(
    "/build",
    methods=("POST",),
)
def build():
    user, *_ = _loader()
    World.build(
        system=request.json.get("system"),
        user=user,
        name=request.json.get("name"),
        desc=request.json.get("desc"),
        backstory=request.json.get("backstory"),
    )

    return get_template_attribute("home.html", "home")(user)


@index_endpoint.route("/build/form", methods=("POST",))
def buildform():
    user, *_ = _loader()
    return get_template_attribute("home.html", "worldbuild")(user=user)


###########################################################
##                    World Routes                       ##
###########################################################
@index_endpoint.route(
    "/world/<string:pk>",
    methods=(
        "GET",
        "POST",
    ),
)
def world(pk):
    user, *_ = _loader()
    world = World.get(pk)
    return get_template_attribute("shared/_gm.html", "home")(user, world)


@index_endpoint.route(
    "/world/<string:pk>/campaigns/manage",
    methods=("GET", "POST"),
)
@index_endpoint.route(
    "/world/<string:pk>/campaigns/manage/<string:campaignpk>",
    methods=("GET", "POST"),
)
def campaignmanage(pk, campaignpk=None):
    user, obj, world, *_ = _loader()
    if user.world_user(world):
        results = requests.post(
            f"http://api:{os.environ.get('COMM_PORT')}/campaign/{campaignpk if campaignpk else ''}",
            json={"user": str(user.pk), "model": obj.model_name(), "pk": str(obj.pk)},
        )
        # log(results.text)
        return results.text
    return "Unauthorized"


@index_endpoint.route("/world/<string:pk>/delete", methods=("POST",))
def worlddelete(pk):
    user, *_ = _loader()
    if world := World.get(pk):
        world.delete()
    return get_template_attribute("home.html", "home")(user)


###########################################################
##                    Model Routes                       ##
###########################################################


@index_endpoint.route(
    "/<string:model>/<string:pk>/<string:page>",
    methods=(
        "GET",
        "POST",
    ),
)
def model(model, pk, page):
    user, obj, *_ = _loader(model=model, pk=pk)
    return get_template(obj, page)(user, obj)


# MARK: Association routes
###########################################################
##                    Association Routes                 ##
###########################################################
@index_endpoint.route(
    "/<string:model>/<string:pk>/associations/<string:modelstr>",
    methods=("GET", "POST"),
)
@index_endpoint.route(
    "/<string:model>/<string:pk>/associations", methods=("GET", "POST")
)
def associations(model, pk, modelstr=None):
    user, obj, *_ = _loader(model=model, pk=pk)
    associations = [
        o
        for o in obj.associations
        if not modelstr or modelstr.lower() == o.model_name().lower()
    ]
    args = dict(request.args) if request.method == "GET" else request.json
    if filter_str := args.get("filter"):
        associations = [o for o in associations if filter_str.lower() in o.name.lower()]
    return get_template_attribute("shared/_associations.html", "associations")(
        user, obj, associations
    )


# MARK: Campaign routes
###########################################################
##                    Association Routes                 ##
###########################################################
@index_endpoint.route(
    "/<string:model>/<string:pk>/campaigns",
    methods=("GET", "POST"),
)
def campaigns(model, pk):
    user, obj, *_ = _loader(model=model, pk=pk)
    args = dict(request.args) if request.method == "GET" else request.json
    campaign = (
        Campaign.get(args.get("campaignpk")) or obj.campaigns[0]
        if obj.campaigns
        else None
    )
    return get_template_attribute("shared/_campaigns.html", "campaigns")(
        user, obj, campaign
    )
