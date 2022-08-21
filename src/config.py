import os
from configparser import RawConfigParser

class Config(object):
    """ ConfigParser provides a basic configuration language which provides a structure similar to 
        Microsoft Windows .INI files
    """
    def __init__(self):
        self.parser = self.build_parser()
        
    def build_parser(self, config_path  : str = "/src/config.ini"):
        """Creates the "parser" object from the "config.ini" file
           
           :param:  `config_path` - path to the "config.ini" file (default: file's root directory)
           :returns: ConfigParser object (with write/read on "config.ini")
        """
        parser = RawConfigParser()
        #path   = os.path.join(os.path.dirname(__file__), config_path)
        path = os.getcwd() + config_path
        #print(path)
        parser.read(path)
        
        
        return parser