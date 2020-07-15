import bpy
#Import a function that checks for pynwb and installs it
from . LibraryChecker import library_checker
library_checker()

#Import class definitions
from . ClassDefinitions import NeuronAnalysis

from . ClassDefinitions import ExplodingBits
from . ClassDefinitions import WriteNWB
from . ClassDefinitions import WideField
from . ClassDefinitions import TwoPhoton
from . ClassDefinitions import RedOpticalChannel
from . ClassDefinitions import GreenOpticalChannel

from . ClassDefinitions import DeviceMenu
from . ClassDefinitions import OpticalChannelMenu

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
    bpy.utils.register_class(WideField)
    bpy.utils.register_class(TwoPhoton)
    bpy.utils.register_class(RedOpticalChannel)
    bpy.utils.register_class(GreenOpticalChannel)
    #This is where registration *should* happen for OpticalChannelGroup, but it doesn't work, so this is currently done in ClassDefinitions
    # bpy.utils.register_class(OpticalChannelGroup)
    # #Associate the OpticalChannelGroup fields with the Scene in an object called 'my_settings"
    # bpy.types.Scene.my_settings = bpy.props.CollectionProperty(type = OpticalChannelGroup)

    
    #menus
    bpy.utils.register_class(DeviceMenu)
    bpy.utils.register_class(OpticalChannelMenu)

    #These strings are used to store values selected from the menus
    bpy.types.Scene.device = bpy.props.StringProperty \
      (name = "Device")
    bpy.types.Scene.wide_field = bpy.props.StringProperty \
      (name = "Wide Field")
    bpy.types.Scene.two_photon = bpy.props.StringProperty \
      (name = "Two Photon")

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
      (name = "Identifier")
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
      (name = "Grid Spacing Units", default = 'mm')
    #Optical Channel Fields - names are set in the Red/Green channel operators
    bpy.types.Scene.optical_channel_name = bpy.props.StringProperty 
    bpy.types.Scene.optical_channel_description = bpy.props.StringProperty
    bpy.types.Scene.emission_lambda = bpy.props.FloatProperty \
      (name = "emission_lambda")

  

#Unregister classes so that they don't clash with other addons
def unregister():
    #main panel
    bpy.utils.unregister_class(NeuronAnalysis)

    #operators
    bpy.utils.unregister_class(ExplodingBits)
    bpy.utils.unregister_class(WriteNWB)
    bpy.utils.unregister_class(WideField)
    bpy.utils.unregister_class(TwoPhoton)
    bpy.utils.unregister_class(RedOpticalChannel)
    bpy.utils.unregister_class(GreenOpticalChannel)

    #menus
    bpy.utils.unregister_class(DeviceMenu)
    bpy.utils.unregister_class(OpticalChannelMenu)

    #Menu options placeholders
    bpy.types.Scene.device 
    
    #Menu options
    bpy.types.Scene.wide_field
    bpy.types.Scene.two_photon 

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

