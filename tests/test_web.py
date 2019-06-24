import subprocess


def test_working():
    result = subprocess.call(['python', '../web.py'])
    assert result == 0