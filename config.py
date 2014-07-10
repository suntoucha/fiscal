# -*- encoding: utf-8 -*-
import yaml
from copy import deepcopy
import os

g_env = os.environ.get('RASBERRY_PI_TORNADO', 'DEVELOPMENT')


def from_yaml(path):
    config = yaml.load(file(path))
    path = [g_env, ]
    v = config[g_env]
    while '_parent' in v:
        p = v['_parent']
        if p in path:
            raise StandardError("Inheritance loop! {}->!!{}!!".format('->'.join(path), p))
        if p not in config:
            raise StandardError('Wrong parrent {}'.format(p))

        path.append(p)
        v = config[p]

    path.reverse()
    res = reduce(merge_dict, map(config.get, path))
    if '_parent' in res:
        del(res['_parent'])

    return res


def merge_dict(a, b):
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = merge_dict(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

if __name__ == '__main__':
    from os.path import dirname, abspath, join
    from pprint import pprint as pp
    pp(
        from_yaml(join(dirname(abspath(__file__)), 'config.yaml'))
    )
