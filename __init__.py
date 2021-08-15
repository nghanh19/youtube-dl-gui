# This Python file uses the following encoding: utf-8

"""
Responsible on how the package looks from the outside.
"""

import os
import sys

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(PATH)))