'''
Created on 15/09/2014

:author: alfred
'''
from performance import Runner
from performance.dynamicmodel import DynamicModelPerformance
from performance.blobfield import BlobFieldPerformance

config = {'DynamicModel': {'test_class': DynamicModelPerformance,
                           'repeats': 5,
                           'params': {'depth': 6, 'children_count': 6}},
          'BlobField': {'test_class': BlobFieldPerformance,
                           'repeats': 5,
                           'params': {'depth': 6, 'children_count': 6}}}

if __name__ == '__main__':

    runner = Runner(config)

    print(runner.run())
