import os

from config import Config
from flask import Flask, get_template_attribute, request

import tasks
from autonomous import log
from autonomous.model.automodel import AutoModel
from autonomous.tasks import AutoTasks
from models.user import User


def create_app():
    app = Flask(os.getenv("APP_NAME", __name__))
    app.config.from_object(Config)

    # Configure Routes
    @app.route(
        "/checktask/<taskid>",
        methods=(
            "GET",
            "POST",
        ),
    )
    def checktask(taskid):
        if task := AutoTasks().get_task(taskid):
            # log(task.status, task.return_value, task.id)
            if task.status == "finished":
                return get_template_attribute("shared/_tasks.html", "completetask")(
                    **task.return_value
                )
            elif task.status == "failed":
                return f"<p>Generation Error for task#: {task.id} </p> </p>{task.result.get('error', '')}</p>"
            else:
                return get_template_attribute("shared/_tasks.html", "checktask")(
                    task.id
                )
        else:
            return "No task found"

    @app.route("/generate/<string:model>/<string:pk>", methods=("POST",))
    def generate(model, pk):
        task = (
            AutoTasks()
            .task(
                tasks._generate_task,
                model=model,
                pk=pk,
            )
            .result
        )
        return get_template_attribute("shared/_tasks.html", "checktask")(task["id"])

    @app.route("/generate/image/<string:model>/<string:pk>", methods=("POST",))
    def image_generate_task(model, pk):
        task = (
            AutoTasks()
            .task(
                tasks._generate_image_task,
                model=model,
                pk=pk,
            )
            .result
        )
        return get_template_attribute("shared/_tasks.html", "checktask")(task["id"])

    return app
