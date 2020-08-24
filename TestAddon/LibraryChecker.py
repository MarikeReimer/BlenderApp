
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import pkg_resources

#This code checks to see if you have pywnb installed and uses pip to install it if you don't.  It is in a separate file to avoid pynwb dependencies
#The original is here: https://blender.stackexchange.com/questions/149944/how-to-write-my-add-on-so-that-when-installed-it-also-installs-dependencies-let/153520#153520 
def library_checker():
    for package in ['pynwb']:  #May want to expand this if I need more libraries
        try:
            dist = pkg_resources.get_distribution(package)
            print('{} ({}) is installed'.format(dist.key, dist.version))
        except pkg_resources.DistributionNotFound:             
            # OS independent (Windows: bin\python.exe; Mac/Linux: bin/python3.7m)
            py_path = Path(sys.prefix) / "bin"
            # first file that starts with "python" in "bin" dir
            py_exec = next(py_path.glob("python*"))
            # ensure pip is installed & update
            subprocess.call([str(py_exec), "-m", "ensurepip"])
            subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
            # install dependencies using pip
            # dependencies such as 'numpy' could be added to the end of this command's list
            subprocess.call([str(py_exec),"-m", "pip", "install", "--user", "pynwb"])
            #from setuptools import setup, find_packages