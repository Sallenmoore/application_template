import io
import random

import requests
from bs4 import BeautifulSoup
from PIL import Image as ImageTools

from autonomous import log
from autonomous.ai.imageagent import ImageAgent
from autonomous.model.autoattr import (
    FileAttr,
    ListAttr,
    ReferenceAttr,
    StringAttr,
)
from autonomous.model.automodel import AutoModel


class Base(AutoModel):
    meta = {"abstract": True, "allow_inheritance": True, "strict": False}

    ################### Class Variables #####################
    ################### Class Methods #####################
    ################### Dunder Methods #####################
    ################### Property Methods #####################
    ################### Crud Methods #####################
    ################### Instance Methods #####################

    ###############################################################
    ##                    VERIFICATION Hooks                     ##
    ###############################################################
    # @classmethod
    # def auto_post_init(cls, sender, document, **kwargs):
    #     super.auto_post_init(sender, document, **kwargs)

    # @classmethod
    # def auto_pre_save(cls, sender, document, **kwargs):
    #     super().auto_pre_save(sender, document, **kwargs)
    #     document.pre_save_example()

    # @classmethod
    # def auto_post_save(cls, sender, document, **kwargs):
    #     super().auto_post_save(sender, document, **kwargs)

    # def clean(self):
    #     super().clean()

    ################### verify methods ##################
    # def pre_save_example(self):
    #     pass
