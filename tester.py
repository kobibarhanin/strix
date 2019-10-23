
import os

os.mkdir('proc_id')
open(f'proc_id/proc_id_config.yaml', 'a').close()

# import yaml
# import io
#
# def set_conf(conf_type, conf, val):
#     with open(f'{conf_type}_config.yaml', 'r') as stream:
#         configs = yaml.safe_load(stream)
#     if configs == None:
#         configs = dict()
#     configs[conf] = val
#     with io.open(f'{conf_type}_config.yaml', 'w') as outfile:
#         yaml.dump(configs, outfile)
#
#
# set_conf("123", 'st','22')