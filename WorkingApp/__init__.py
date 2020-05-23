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



def register():
    bpy.utils.register_class(NeuronAnalysis)
    bpy.utils.register_class(ExplodingBits)
    bpy.types.Scene.my_string_prop = bpy.props.StringProperty \
      (
        name = "My String",
        description = "My description",
        default = "default"
      )

def unregister():
    bpy.utils.unregister_class(NeuronAnalysis)
    bpy.utils.unregister_class(ExplodingBits)
    bpy.types.Scene.my_string_prop
    
