'''
Created on 15/09/2014

:author: alfred
'''
from dirty_models.models import BaseModel
from dirty_models.fields import BlobField
from performance.dynamicmodel import create_dict


class FakeDynModel(BaseModel):
    fake_data = BlobField()


class BlobFieldPerformance:

    def __init__(self, depth=5, children_count=5):
        self.depth = depth
        self.children_count = children_count

    def prepare(self):
        self.data = create_dict(self.depth, self.children_count)

    def run(self):
        return FakeDynModel(data={'fake_data': self.data})
