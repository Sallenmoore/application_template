import io
import os

import requests
from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    session,
)

from autonomous import log
from autonomous.auth import AutoAuth, auth_required

index_page = Blueprint("index", __name__)


def _authenticate(user, obj):
    if user in obj.get_world().users:
        return True
    return False


# def update_with_session(requestdata):
#     # log(requestdata)
#     args = requestdata.copy()
#     args["scenepk"] = requestdata.get("scenepk") or session.get("scenepk")
#     return args


@index_page.route("/", endpoint="index", methods=("GET", "POST"))
@index_page.route("/home", endpoint="index", methods=("GET", "POST"))
@auth_required()
def index():
    user = AutoAuth.current_user()
    for w in World.all():
        w.users += [user]
        w.save()

    user = AutoAuth.current_user()
    session["page"] = "/home"
    return render_template("index.html", user=user, page_url="/home")

@index_page.route("/<string:model>/<string:pk>", methods=("GET", "POST"))
@index_page.route("/<string:model>/<string:pk>/<path:page>", methods=("GET", "POST"))
@auth_required(guest=True)
def page(model, pk, page=""):
    user = AutoAuth.current_user()
    session["page"] = f"/{model}/{pk}/{page or 'details'}"
    if obj := World.get_model(model, pk):
        session["model"] = model
        session["pk"] = pk
    return render_template("index.html", user=user, obj=obj, page_url=session["page"])


@index_page.route(
    "/api/<path:rest_path>",
    endpoint="api",
    methods=(
        "GET",
        "POST",
    ),
)
# @auth_required(guest=True)
def api(rest_path):
    url = f"http://api:{os.environ.get('COMM_PORT')}/{rest_path}"
    response = "<p>You do not have permission to alter this object<p>"
    # log(request.method)
    user = AutoAuth.current_user()
    if request.method == "GET":
        rest_path = request.path.replace("/api/", "")
        params = dict(request.args)
        params["user"] = user.pk
        url = f"http://api:{os.environ.get('COMM_PORT')}/{rest_path}?{requests.compat.urlencode(params)}"
        log("API GET REQUEST", url)
        response = requests.get(url).text
    elif not user.is_guest:
        log("API POST REQUEST", rest_path, request.json)
        if "admin/" in url and user.is_admin:
            response = requests.post(url, json=request.json).text
        elif request.json.get("model") and request.json.get("pk"):
            obj = World.get_model(request.json.get("model"), request.json.get("pk"))
            if _authenticate(user, obj):
                response = requests.post(url, json=request.json).text
        else:
            response = requests.post(url, json=request.json).text
    # log(response)
    return response


@index_page.route("/task/<path:rest_path>", endpoint="tasks", methods=("POST",))
@auth_required()
def tasks(rest_path):
    user = AutoAuth.current_user()
    obj = World.get_model(request.json.get("model")).get(request.json.get("pk"))
    if _authenticate(user, obj):
        log(request.json)
        response = requests.post(
            f"http://tasks:{os.environ.get('COMM_PORT')}/{rest_path}", json=request.json
        )
        # log(response.text)
    return response.text
