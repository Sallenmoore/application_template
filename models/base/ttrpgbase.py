import inspect
import random
import traceback

import markdown
import validators
from flask import get_template_attribute
from slugify import slugify

from autonomous import log
from autonomous.db import ValidationError
from autonomous.model.autoattr import IntAttr, ReferenceAttr, StringAttr
from autonomous.model.automodel import AutoModel
from models.images.image import Image
from models.journal import Journal

MAX_NUM_IMAGES_IN_GALLERY = 100
IMAGES_BASE_PATH = "static/images/tabletop"


class TTRPGBase(AutoModel):
    """
    TTRPGBase is a base class for tabletop role-playing game (TTRPG) models. It provides common attributes and methods for various TTRPG entities such as characters, locations, items, etc.
    """

    meta = {"abstract": True, "allow_inheritance": True, "strict": False}
    name = StringAttr(default="")
    backstory = StringAttr(default="")
    backstory_summary = StringAttr(default="")
    desc = StringAttr(default="")
    desc_summary = StringAttr(default="")
    traits = StringAttr(default="")
    image = ReferenceAttr(choices=[Image])
    current_age = IntAttr(default=lambda: random.randint(18, 50))
    history = StringAttr(default="")
    journal = ReferenceAttr(choices=[Journal])

    story_types = [
        "tragic",
        "heroic",
        "mysterious",
        "sinister",
        "unexpected",
        "dangerous",
        "boring",
        "mundane",
        "opulent",
        "decaying",
        "haunted",
        "harrowing",
        "enchanted",
        "cursed",
    ]

    child_list = {"city": "cities"}
    _no_copy = {
        "journal": None,
        "history": "",
    }
    _traits_list = [
        "secretly evil",
        "openly evil",
        "openly neutral",
        "secretly neutral",
        "openly good",
        "secretly good",
        "dangerous",
        "mysterious",
    ]
    _funcobj = {}

    ########### Dunder Methods ###########

    def __eq__(self, obj):
        if not hasattr(obj, "pk"):
            return False
        try:
            return self.pk == obj.pk
        except Exception as e:
            # traceback.print_stack(limit=5)
            log(e)
            return False

    def __ne__(self, obj):
        if not hasattr(obj, "pk"):
            return True
        if hasattr(obj, "pk"):
            return self.pk != obj.pk
        return True

    def __lt__(self, obj):
        if hasattr(obj, "name"):
            return self.name < obj.name
        return False

    def __gt__(self, obj):
        if hasattr(obj, "name"):
            return self.name > obj.name
        return False

    def __hash__(self):
        return hash(self.pk)

    ########### Class Methods ###########

    @classmethod
    def child_list_key(cls, model):
        return cls.child_list.get(model.lower(), f"{model.lower()}s") if model else None

    @classmethod
    def all_models_str(cls):
        return [m.__name__ for m in cls.all_models()]

    @classmethod
    def all_models(cls):
        subclasses = TTRPGBase.__subclasses__()
        TTRPGObject = [s for s in subclasses if s.__name__ == "TTRPGObject"][0]
        result = cls.all_subclasses(TTRPGObject)
        return result

    @classmethod
    def all_subclasses(cls, BaseModel=None):
        """
        Recursively retrieves all non-abstract subclasses of the given class.

        This method starts with the given class (or the class on which the method
        is called if no class is provided) and traverses its subclass hierarchy
        to find all subclasses that are not marked as abstract.

        Args:
            BaseModel (type, optional): The base class to start the search from.
                If not provided, the method uses the class on which it is called.

        Returns:
            list: A list of all non-abstract subclasses of the given class.
        """
        if not BaseModel:
            BaseModel = cls
        subclasses = BaseModel.__subclasses__()
        models = []
        for subclass in subclasses:
            if "_meta" in subclass.__dict__ and not subclass._meta.get("abstract"):
                models.append(subclass)
            models += cls.all_subclasses(subclass)
        return models

    @classmethod
    def get_model(cls, model, pk=None):
        """
        Retrieve a model class or an instance of the model class by its primary key.

        This method searches through all subclasses of `TTRPGBase` to find a model class
        that matches the provided `model` name. If a primary key (`pk`) is provided, it
        returns an instance of the model class with that primary key. Otherwise, it returns
        the model class itself.

        Args:
            model (str): The name of the model class to retrieve.
            pk (int, optional): The primary key of the model instance to retrieve. Defaults to None.

        Returns:
            Model class or instance: The model class if `pk` is None, otherwise an instance of the model class.

        Raises:
            AttributeError: If the model class does not have a `get` method.
            ValueError: If the provided `model` is not a string or is None.
        """
        # log(model, pk)
        if not model or not isinstance(model, str):
            return model
        Model = None
        for klass in TTRPGBase.all_subclasses():
            # log(klass)
            if klass.__name__.lower() == model.lower():
                Model = klass
        return Model.get(pk) if Model and pk else Model

    @classmethod
    def get_models(cls):
        """
        Class method to retrieve a list of models.

        This method iterates over the class attribute `_models`, which is expected to be a list of model identifiers (strings),
        and loads each model using the `AutoModel.load_model` method.

        Returns:
            list: A list of loaded models.
        """
        return cls.all_models()

    ########### Property Methods ###########
    @property
    def age(self):
        return self.current_age

    @age.setter
    def age(self, value):
        self.current_age = value

    @property
    def child_models(self):
        results = []
        for model in self.all_models():
            if self.model_name() in model.association_list:
                results.append(model)
        return results

    @property
    def current_date(self):
        return self.world.current_date

    @property
    def description(self):
        return self.desc

    @description.setter
    def description(self, val):
        self.desc = val

    @property
    def description_summary(self):
        return self.desc_summary

    @description_summary.setter
    def description_summary(self, val):
        self.desc_summary = val

    @property
    def funcobj(self):
        self._funcobj["parameters"]["required"] = list(
            self._funcobj["parameters"]["properties"].keys()
        )
        return self._funcobj

    @property
    def geneology(self):
        # TBD: Implement geneology
        return [self]

    @property
    def genres(self):
        return list(self._systems.keys())

    @property
    def history_primer(self):
        return f"Incorporate the below EVENTS into the given {self.title}'s HISTORY to generate a narrative summary of the {self.title}'s story. Use MARKDOWN format with paragraph breaks after no more than 4 sentences."

    @property
    def history_prompt(self):
        if self.backstory_summary:
            return f"""
HISTORY
---
{self.backstory_summary}

EVENTS
---
"""

    @property
    def image_tags(self):
        return [self.genre, self.model_name().lower()]

    @property
    def image_prompt(self):
        return self.desc

    @property
    def path(self):
        return f"{self.model_name().lower()}/{self.pk}"

    @property
    def possible_events(self):
        return self._possible_events

    @property
    def motif(self):
        return self.traits

    @property
    def map_thumbnail(self):
        return self.map.image.url(100)

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def title(self):
        return self.get_title(self)

    @property
    def titles(self):
        return self.system._titles

    ########### CRUD Methods ###########
    def delete(self):
        if self.journal:
            self.journal.delete()
        if self.image:
            self.image.delete()
        if self.map:
            self.map.delete()
        return super().delete()

    # MARK: Generate
    def generate(self, prompt=""):
        # log(f"Generating data with AI for {self.name} ({self})...", _print=True)
        prompt += f"""
Use and expand on the existing object data listed below for the {self.title} object:
{"- Name: " + self.name if self.name.strip() else ""}
{"- Theme: " + self.traits if self.traits else ""}
{"- Goal: " + self.goal if getattr(self, "goal", None) else ""}
{"- Current Status: " + self.status if getattr(self, "status", None) else ""}
{"- Description: "+self.description.strip() if self.description.strip() else ""}
{"- Backstory: " + self.backstory.strip() if self.backstory.strip() else ""}
        """
        if associations := [*self.geneology, *self.children]:
            prompt += """
===
- Associated Objects:
"""
            for ass in associations:
                if ass.name and ass.backstory_summary:
                    prompt += f"""
    - pk: {ass.pk}
        - Model: {ass.model_name()}
        - Type: {ass.title}
        - Name: {ass.name}
        - Backstory: {ass.backstory_summary}
"""
        name = self.name
        if results := self.system.generate(self, prompt=prompt, funcobj=self.funcobj):
            # log(results, _print=True)
            if notes := results.pop("notes", None):
                if not self.journal:
                    self.journal = Journal(world=self.get_world(), parent=self)
                    self.journal.save()
                    self.save()
                for idx, note in enumerate(notes):
                    self.journal.add_entry(
                        title=f"SECRET #{idx+1}",
                        text=note,
                        importance=1,
                    )
            for k, v in results.items():
                setattr(self, k, v)
            if name:
                self.backstory = self.backstory.replace(self.name, name)
                self.desc = self.desc.replace(self.name, name)
                self.name = name
            self.save()
        else:
            log(results, _print=True)

        return results

    ############# Boolean Methods #############

    def is_child(self, obj):
        return self in obj.children

    def is_associated(self, obj):
        return obj in self.associations

    ############# Image Methods #############

    def get_image_list(self, tags=[]):
        """
        Retrieve a list of images that match the given tags.
        Args:
            tags (list, optional): A list of tags to filter images by. If not provided,
                                   defaults to a list containing the model's name in lowercase.
        Returns:
            list: A list of images that contain all the specified tags.
        """

        images = []
        tags = tags or [self.model_name().lower()]
        images = [img for img in Image.all() if all(t in img.tags for t in tags)]
        return images

    # MARK: generate_image
    def generate_image(self):
        prompt = f"""Set in the year {self.get_world().current_date}.

{self.image_prompt}
"""
        self.image = Image.generate(prompt=prompt, tags=self.image_tags)
        self.image.save()
        self.save()
        return self.image

    def get_map_list(self):
        images = []
        for img in Image.all():
            # log(img.asset_id)
            if all(
                t in img.tags for t in ["map", self.model_name().lower(), self.genre]
            ):
                images.append(img)
        return images

    # MARK: generate_map
    def generate_map(self):
        log("Generating map...", _print=True)
        self.map = Image.generate(
            prompt=self.map_prompt or self.system.map_prompt(self),
            tags=["map", self.model_name().lower(), self.genre],
            img_quality="hd",
            img_size="1792x1024",
        )
        log("Map Generated.", _print=True)
        self.map.save()
        self.save()
        return self.map

    ############# Association Methods #############
    # MARK: Associations
    def add_association(self, obj):
        # log(len(obj.associations), self in obj.associations)
        if self not in obj.associations:
            obj.associations += [self]
            obj.save()
        # log(len(obj.associations), self in obj.associations)

        # log(len(self.associations), obj in self.associations)
        if obj not in self.associations:
            self.associations += [obj]
            self.save()
        # log(len(self.associations), obj in self.associations)
        return obj

    def add_associations(self, objs):
        for obj in objs:
            self.add_association(obj)
        return self.associations

    def remove_association(self, obj):
        if obj in self.associations:
            self.associations.remove(obj)
            self.save()
            obj.remove_association(self)
        return self.associations

    def has_associations(self, model):
        if not isinstance(model, str):
            model = model.__name__
        for assoc in self.associations:
            if assoc.model_name() == model:
                return True
        return False

    ########## Object Data ######################
    # MARK: History
    def resummarize(self, upload=False):
        self.history = "Generating... please refresh the page in a few seconds."
        self.save()
        # generate backstory summary
        if len(self.backstory) < 250:
            self.backstory_summary = self.backstory
        else:
            primer = "Generate a summary of less than 250 words of the following events in MARKDOWN format with paragraph breaks where appropriate, but after no more than 4 sentences."
            self.backstory_summary = self.system.generate_summary(
                self.backstory, primer
            )
            self.backstory_summary = markdown.markdown(self.backstory_summary)
        # generate backstory summary
        if len(self.description.split()) < 15:
            self.description_summary = self.description
        else:
            primer = f"Generate a plain text summary of the provided {self.title}'s description in 15 words or fewer."
            self.description_summary = self.system.generate_summary(
                self.description, primer
            )
        self.save()

        # generate history
        if self.history_prompt:
            history = self.system.generate_summary(
                self.history_prompt, self.history_primer
            )
            history = history.replace("```markdown", "").replace("```", "")
            self.history = (
                markdown.markdown(history).replace("h1>", "h3>").replace("h2>", "h3>")
            )
            self.save()

    def get_title(self, model):
        if inspect.isclass(model):
            model = model.__name__
        elif not isinstance(model, str):
            model = model.__class__.__name__
        model = model.lower()
        return self.system._titles.get(model, model.capitalize())

    def get_icon(self, model):
        if inspect.isclass(model):
            model = model.__name__
        elif not isinstance(model, str):
            model = model.__class__.__name__
        model = model.lower()
        return self.system._icons.get(model, "line-md:question")

    def page_data(self):
        return {}

    def add_journal_entry(
        self,
        pk=None,
        title=None,
        text=None,
        tags=[],
        importance=0,
        date=None,
        associations=[],
    ):
        if pk:
            return self.journal.update_entry(
                pk=pk,
                title=title,
                text=text,
                tags=tags,
                importance=importance,
                date=date,
                associations=associations,
            )
        else:
            return self.journal.add_entry(
                title=title,
                text=text,
                tags=tags,
                importance=importance,
                date=date,
                associations=associations,
            )

    def search_autocomplete(self, query):
        results = []
        for model in self.all_models():
            Model = self.load_model(model)
            # log(model, query)
            results += [
                r for r in Model.search(name=query, world=self.get_world()) if r != self
            ]
            # log(results)
        return results

    # /////////// HTML SNIPPET Methods ///////////
    def snippet(self, user, macro, kwargs=None):
        module = f"models/_{self.model_name().lower()}.html"
        kwargs = kwargs or {}
        # try:
        return get_template_attribute(module, macro)(user, self, **kwargs)
        # except Exception as e:
        #     log(e)
        #     return ""

    ## MARK: - Verification Methods
    ###############################################################
    ##                    VERIFICATION HOOKS                   ##
    ###############################################################

    @classmethod
    def auto_pre_save(cls, sender, document, **kwargs):
        super().auto_pre_save(sender, document, **kwargs)
        document.pre_save_image()
        document.pre_save_backstory()
        document.pre_save_traits()

    @classmethod
    def auto_post_save(cls, sender, document, **kwargs):
        super().auto_post_save(sender, document, **kwargs)
        document.post_save_journal()

    ###############################################################
    ##                    VERIFICATION HOOKS                     ##
    ###############################################################

    def pre_save_image(self):
        if isinstance(self.image, str):
            if self.image.startswith("/static"):
                ##### MIGRATION #####
                self.image = Image.from_url(
                    f"https://world.stevenamoore.dev{self.image}",
                    prompt=self.image_prompt,
                    tags=[*self.image_tags],
                )
            elif validators.url(self.image):
                self.image = Image.from_url(
                    self.image,
                    prompt=self.image_prompt,
                    tags=[*self.image_tags],
                )
                self.image.save()
            elif image := Image.get(self.image):
                self.image = image
            else:
                raise ValidationError(
                    f"Image must be an Image object, url, or Image pk, not {self.image}"
                )
        elif self.image and not self.image.tags:
            self.image.tags = self.image_tags
            self.image.save()
        # log(self.image)

    def pre_save_backstory(self):
        if not self.backstory:
            self.backstory = f"A {self.traits} {self.title}."
        self.backstory_summary = self.backstory_summary.replace("h1>", "h3>").replace(
            "h2>", "h3>"
        )

    def pre_save_traits(self):
        if not self.traits:
            self.traits = random.choice(self._traits_list)

    def post_save_journal(self):
        if not self.journal:
            self.journal = Journal(world=self.get_world(), parent=self)
            self.journal.save()
            self.save()
