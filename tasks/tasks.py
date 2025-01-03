import json

from autonomous import log
from autonomous.model.automodel import AutoModel
from autonomous.tasks import AutoTasks
from models.user import User



####################################################################################################
# Tasks
####################################################################################################
def _generate_task(model, pk):
    if Model := World.get_model(model):
        obj = Model.get(pk)
        obj.generate()
        if not obj.image:
            AutoTasks().task(
                _generate_image_task,
                model,
                pk,
            )
    return {"url": f"/api/manage/{obj.path}"}

def _generate_image_task(model, pk):
    if Model := World.get_model(model):
        obj = Model.get(pk)
        obj.resummarize()
        obj.generate_image()
    return {"url": f"/api/{obj.path}/details"}
