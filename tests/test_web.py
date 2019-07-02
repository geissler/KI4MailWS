import subprocess
import sys
import os



def test_working():

    result = subprocess.call(['python', '../web.py'])
    assert result == 0