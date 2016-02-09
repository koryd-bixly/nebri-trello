import logging
from nebriosmodels import NebriOSField, NebriOSModel

logging.basicConfig(filename='TestModel.log', level=logging.DEBUG)


class TestModel(NebriOSModel):
    number = NebriOSField()
    name = NebriOSField()