import yaml
import logging
import os
import sys

#####
# Configuration class - exposes a yaml field that contains the YAML configuration
#
class Config(object):
    def __init__(self, configfile=None):
        self.logger = logging.getLogger("e3e.harvester.config")
        self.logger.setLevel(logging.INFO)
        if configfile is None:
            self.logger.warn("Current path "+os.getcwd())
            self.configfile = os.path.join(os.getcwd(),
                                           'harvester.yml')
        try:
            self.yaml = yaml.load(file(self.configfile, 'r'))
        except yaml.YAMLError, exc:
            self.logger.error("Error in YAML configuration file:", exc)
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                self.logger.error("YAML error position: (%s:%s)" % (mark.line+1, mark.column+1)) 
            sys.exit(1)

