# https://stackoverflow.com/questions/46285550/relative-path-to-files-in-gnu-radio-companion
#
# this module will be imported in the into your flowgraph
# GNU Radio Companion (GRC) paths are relative to where GRC is started.
#
# If the script is intended to be run from its containing directory, a "Python Module" block can be added to GRC with the contents:

import os

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)
