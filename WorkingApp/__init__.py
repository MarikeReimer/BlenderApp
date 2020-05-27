# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "TestAddon",
    "author" : "Marike",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


import bpy
from . ClassDefinitions   import NeuronAnalysis
from . ClassDefinitions  import ExplodingBits
from .ClassDefinitions import WriteNWB
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import pkg_resources


#This code checks to see if you have pywnb installed and uses pip to install it if you don't
for package in ['pynwb']:  #May want to expand this if I need more libraries
    try:
        dist = pkg_resources.get_distribution(package)
        print('{} ({}) is installed'.format(dist.key, dist.version))
    except pkg_resources.DistributionNotFound:
        
        #This code installs pynwb from here: https://blender.stackexchange.com/questions/149944/how-to-write-my-add-on-so-that-when-installed-it-also-installs-dependencies-let/153520#153520

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




def register():
    bpy.utils.register_class(NeuronAnalysis)
    bpy.utils.register_class(ExplodingBits)
    bpy.utils.register_class(WriteNWB)

    #Subject Table Strings
    bpy.types.Scene.subject_id = bpy.props.StringProperty \
      (name = "Subject ID")
    bpy.types.Scene.age = bpy.props.StringProperty \
      (name = "Age")
    bpy.types.Scene.subject_description = bpy.props.StringProperty \
      (name = "Description")
    bpy.types.Scene.genotype = bpy.props.StringProperty \
      (name = "Genotype")
    bpy.types.Scene.sex = bpy.props.StringProperty \
      (name = "Sex")
    bpy.types.Scene.species = bpy.props.StringProperty \
      (name = "Species")
    #NWBfile fields
    bpy.types.Scene.identifier = bpy.props.StringProperty \
      (name = "Identifier")
    bpy.types.Scene.session_start_time = bpy.props.StringProperty \
      (name = "Session Start Time")
    bpy.types.Scene.session_description = bpy.props.StringProperty \
      (name = "Session Description")

def unregister():
    bpy.utils.unregister_class(NeuronAnalysis)
    bpy.utils.unregister_class(ExplodingBits)
    bpy.utils.unregister_class(WriteNWB)
    bpy.types.Scene.subject_id
    bpy.types.Scene.age
    bpy.types.Scene.subject_description
    bpy.types.Scene.sex
    bpy.types.Scene.species
    
