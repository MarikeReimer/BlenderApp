import bpy

#Used for importing dropdown menu pieces
# from bpy.types import Panel, PropertyGroup, Scene, WindowManager
# from bpy.props import (
#     IntProperty,
#     EnumProperty,
#     StringProperty,
#     PointerProperty,
# )

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
    #main panel
    bpy.utils.register_class(NeuronAnalysis)
    #operators
    bpy.utils.register_class(ExplodingBits)
    bpy.utils.register_class(WriteNWB)
        
    #Subject Table fields
    bpy.types.Scene.subject_id = bpy.props.StringProperty \
      (name = "Subject ID", default = "Anm_")
    bpy.types.Scene.age = bpy.props.StringProperty \
      (name = "Age", default = "PD#")
    bpy.types.Scene.subject_description = bpy.props.StringProperty \
      (name = "Description", default = 'fuzzy')
    bpy.types.Scene.genotype = bpy.props.StringProperty \
      (name = "Genotype", default = 'B6')
    bpy.types.Scene.sex = bpy.props.StringProperty \
      (name = "Sex", default = "F")
    bpy.types.Scene.species = bpy.props.StringProperty \
      (name = "Species", default = "Mus musculus")
    #NWBfile fields
    bpy.types.Scene.identifier = bpy.props.StringProperty \
      (name = "Identifier", default = 'findme')
    bpy.types.Scene.session_start_time = bpy.props.StringProperty \
      (name = "Session Start Time", default = "hard coded")
    bpy.types.Scene.session_description = bpy.props.StringProperty \
      (name = "Session Description", default = "We imaged neurons")
    #Imaging Plane Fields
    bpy.types.Scene.plane_name = bpy.props.StringProperty \
      (name = "Plane Name", default = "my plane")
    bpy.types.Scene.plane_description = bpy.props.StringProperty \
      (name = "Plane Description", default = "plane description")
    bpy.types.Scene.excitation_lambda = bpy.props.StringProperty \
      (name = "Excitation Lambda")
    bpy.types.Scene.imaging_rate = bpy.props.StringProperty \
      (name = "Imaging Rate")
    bpy.types.Scene.indicator = bpy.props.StringProperty \
      (name = "Indicator", default = "YFP")
    bpy.types.Scene.location = bpy.props.StringProperty \
      (name = "Location", default = "spinal cord")
    bpy.types.Scene.grid_spacing = bpy.props.StringProperty \
      (name = "Grid Spacing", default = "hard coded")
    bpy.types.Scene.grid_spacing_unit = bpy.props.StringProperty \
      (name = "Grid Spacing Units", default = 'um')
    #Fields that would do better in a dropdown
    bpy.types.Scene.device = bpy.props.StringProperty \
      (name = "Device", default = "2 Photon")
    bpy.types.Scene.optical_channel_name = bpy.props.StringProperty \
      (name = "Optical Channel Name", default = "Green")
    bpy.types.Scene.optical_channel_description = bpy.props.StringProperty \
      (name = "Optical Channel Description", default = "Channel for YFP")
    bpy.types.Scene.emission_lambda = bpy.props.FloatProperty \
      (name = "emission_lambda")
    # bpy.types.Scene.wavelength = bpy.props.FloatProperty \
    #   (name = "wavelength")
    
  

#Unregister classes so that they don't clash with other addons
def unregister():
    #main panel
    bpy.utils.unregister_class(NeuronAnalysis)

    #operators
    bpy.utils.unregister_class(ExplodingBits)
    bpy.utils.unregister_class(WriteNWB)

    #Subject fields
    bpy.types.Scene.subject_id
    bpy.types.Scene.age
    bpy.types.Scene.subject_description
    bpy.types.Scene.sex
    bpy.types.Scene.species
    #NWBFile fields
    bpy.types.Scene.identifier
    bpy.types.Scene.session_start_time
    bpy.types.Scene.session_description

    #Imaging plane fields
    bpy.types.Scene.plane_name
    bpy.types.Scene.plane_description
    bpy.types.Scene.excitation_lambda
    bpy.types.Scene.imaging_rate
    bpy.types.Scene.indicator
    bpy.types.Scene.location
    bpy.types.Scene.grid_spacing
    bpy.types.Scene.grid_spacing_unit
    bpy.types.Scene.optical_channel_name
    bpy.types.Scene.optical_channel_description
    bpy.types.Scene.emission_lambda
    # bpy.types.Scene.wavelength



