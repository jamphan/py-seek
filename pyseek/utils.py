import logging.config
import os
import yaml

def clean_host_str(host):
    for ftr in ["https://", "http://", "/"]:
        host = host.strip(ftr)
    return host

def get_yaml_config(yaml_file):
    with open(yaml_file, 'r') as fd:
        try:
            return yaml.safe_load(fd)
        except yaml.YAMLError as ex:
            raise ex

def get_logging_dictconfig(logconfig=None, clear_log=False):

    if logconfig==None:
        src_dir = os.path.dirname(__file__)
        logconfig = os.path.join(src_dir, 'config', 'logging.yml')

    config = get_yaml_config(logconfig)

    if clear_log:
        open(config['handlers']['file']['filename'], 'w').close()

    logging.config.dictConfig(config)
