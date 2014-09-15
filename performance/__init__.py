from datetime import datetime, timedelta
from sys import setrecursionlimit
from functools import reduce


class Runner:

    def __init__(self, config):
        self.config = config

    def run(self):
        setrecursionlimit(9999999)

        result = {}
        for label, data in self.config.items():
            test = data['test_class'](**data['params'])
            test.prepare()
            result_test = []
            print ('{0} start'.format(label))
            for i in range(data.get('repeats', 1)):
                print ('{0}: iteration no. {1} start'.format(label, i))
                time_start = datetime.now()
                test.run()
                time_stop = datetime.now()
                elapsed = time_stop - time_start
                print ('{0}: iteration no. {1} => {2}'.format(label, i, str(elapsed)))
                result_test.append(elapsed)
            total = reduce(lambda acc, x: acc + x, result_test, timedelta())
            print ('{0} => {1}'.format(label, str(total)))
            result[label] = {'results': result_test, 'total': total}

        return result
