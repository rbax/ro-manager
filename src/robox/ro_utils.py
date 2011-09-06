# ro_utils.py

"""
Research Object management supporting utility functions
"""

import os.path
import json
import re

CONFIGFILE = ".ro_config"

def ronametoident(name):
    """
    Turn resource object name into an identifier containing only letters, digits and underscore characters
    """
    name = re.sub(r"\s", '_', name)         # spaces, etc. -> underscores
    name = re.sub(r"\W", "", name)          # Non-identifier characters -> remove
    return name

def progname(args):
    return os.path.basename(args[0])

def ropath(ro_config, dir):
    rodir  = os.path.abspath(dir)
    robase = ro_config['robase']
    if os.path.isdir(rodir) and os.path.commonprefix([robase, rodir]) == robase:
       return rodir
    return None
    
def configfilename(configbase):
    return os.path.abspath(configbase+"/"+CONFIGFILE)

def writeconfig(configbase, config):
    """
    Write supplied configuration dictionary to indicated directory
    """
    configfile = open(configfilename(configbase), 'w')
    json.dump(config, configfile, indent=4)
    configfile.write("\n")
    configfile.close()
    return

def resetconfig(configbase):
    """
    Reset configuration in indicated directory
    """
    ro_config = {
        "robase":     None,
        "roboxuri":   None,
        "roboxpass":  None,
        "username":   None,
        "useremail":  None
        }
    writeconfig(configbase, ro_config)
    return

def readconfig(configbase):
    """
    Read configuration in indicated directory and return as a dictionary
    """
    ro_config = {
        "robase":     None,
        "roboxuri":   None,
        "roboxpass":  None,
        "username":   None,
        "useremail":  None
        }
    configfile = open(configfilename(configbase), 'r')
    try:
        ro_config = json.load(configfile)
    finally:
        configfile.close()
    return ro_config

# End.
