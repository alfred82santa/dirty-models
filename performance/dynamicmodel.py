'''
Created on 15/09/2014

:author: alfred
'''
from dirty_models.models import DynamicModel, BaseModel
from dirty_models.fields import ModelField


def create_dict(depth=5, children_count=5):
    if depth > 0:
        return {'test_{0}'.format(i): create_dict(depth - 1, children_count) for i in range(children_count)}
    else:
        return 'top'


class FakeDynModel(BaseModel):
    fake_data = ModelField(model_class=DynamicModel)


class DynamicModelPerformance:

    def __init__(self, depth=5, children_count=5):
        self.depth = depth
        self.children_count = children_count

    def prepare(self):
        self.data = create_dict(self.depth, self.children_count)

    def run(self):
        return FakeDynModel(data={'fake_data': self.data})
