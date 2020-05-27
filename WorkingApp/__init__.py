import bpy
#Import a function that checks for pynwb and installs it
from . LibraryChecker import library_checker
library_checker()

#Import class definitions
from . ClassDefinitions import NeuronAnalysis
from . ClassDefinitions import ExplodingBits
from . ClassDefinitions import WriteNWB

#Information about the Addon created by the Blender Development VSCode Extension
bl_info = {
    "name" : "TestAddon",
    "author" : "Marike",
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

#Register classes so that Blender can find them
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


#Unregister classes so that they don't clash with other addons
def unregister():
    bpy.utils.unregister_class(NeuronAnalysis)
    bpy.utils.unregister_class(ExplodingBits)
    bpy.utils.unregister_class(WriteNWB)
    bpy.types.Scene.subject_id
    bpy.types.Scene.age
    bpy.types.Scene.subject_description
    bpy.types.Scene.sex
    bpy.types.Scene.species
    
