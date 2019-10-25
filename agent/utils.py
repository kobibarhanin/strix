import yaml
import io

def get_conf(conf_type, conf):
    try:
        with open(f'{conf_type}_config.yaml', 'r') as stream:
            configs = yaml.safe_load(stream)
        return configs[conf]
    except Exception:
        print(f'No configuration for: {conf}')
        return None


def set_conf(conf_type, conf, val):
    with open(f'{conf_type}_config.yaml', 'r') as stream:
        configs = yaml.safe_load(stream)
    if configs == None:
        configs = dict()
    configs[conf] = val
    with io.open(f'{conf_type}_config.yaml', 'w') as outfile:
        yaml.dump(configs, outfile)