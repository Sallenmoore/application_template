from flask import request

from autonomous import log
from autonomous.models.automodel import AutoModel
from models.user import User


def loader(
    user=None,
    model=None,
    pk=None,
    macro=None,
    module=None,
):
    # log(f"User: {user}, Model: {model}, PK: {pk}")
    # log(f"Request: {request}")
    if request.method == "GET":
        request_data = request.args
        # log(f"get request: {request_data}")
    elif request.method == "POST":
        request_data = request.json
        # log(f"post: {request_data}")
    else:
        return None, None, None, None, None

    # get user
    if not user:
        user_data = request_data.get("user", None)
        #
        user = (
            User.get(user_data["pk"])
            if isinstance(user_data, dict) and user_data.get("pk")
            else User.get(user_data)
        )
    else:
        user = User.get(user)
    # log(user)
    # get obj
    obj = AutoModel.get_model(
        model or request_data.get("model", None), pk or request_data.get("pk", None)
    )
    # log(obj)
    # get world
    return user, obj
