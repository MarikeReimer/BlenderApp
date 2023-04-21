from email.policy import default
import bpy
from datetime import datetime

#Import class definitions
from . ClassDefinitions import NeuronAnalysis
from . ClassDefinitions import ExplodingBits
from . ClassDefinitions import SpinesToCollections
from . ClassDefinitions import BoundingBoxes
from . ClassDefinitions import AutoSegmenter
from . ClassDefinitions import DiscSegmenter
from . ClassDefinitions import ManualLength
from . ClassDefinitions import ManualMerge
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
    bpy.utils.register_class(SpinesToCollections)
    bpy.utils.register_class(BoundingBoxes)
    bpy.utils.register_class(AutoSegmenter)
    bpy.utils.register_class(DiscSegmenter)
    bpy.utils.register_class(ManualLength)
    bpy.utils.register_class(ManualMerge)
    bpy.utils.register_class(WriteNWB)
  
        
    #Subject Table fields
    bpy.types.Scene.subject_id = bpy.props.StringProperty \
      (name = "Subject ID", default = "Anm_")
    bpy.types.Scene.age = bpy.props.StringProperty \
      (name = "Age", default = "P#D")
    #bpy.types.Scene.subject_description = bpy.props.StringProperty \
    #  (name = "Description", default = 'fuzzy')
    bpy.types.Scene.genotype = bpy.props.StringProperty \
      (name = "Genotype", default = 'Thy1-YFP')
    bpy.types.Scene.sex = bpy.props.StringProperty \
      (name = "Sex", default = "F")
    bpy.types.Scene.species = bpy.props.StringProperty \
      (name = "Species", default = "Mus musculus")
    bpy.types.Scene.strain = bpy.props.StringProperty \
      (name = "Strain", default = "C57BL/6")
    #NWBfile fields
    bpy.types.Scene.experiment_description = bpy.props.StringProperty \
      (name = "Experiment Description", default = 'We studied the efficacy of romidepsin as a treatment to reduce spasticity and abnormal dendritic spine growth following a contusion injury.')    
    bpy.types.Scene.experimenter = bpy.props.StringProperty \
      (name = "Experimenter", default = "Sierra Kauer")
    bpy.types.Scene.identifier = bpy.props.StringProperty \
      (name = "Identifier", default = 'Neuron#_Dendrite#')
    bpy.types.Scene.institution = bpy.props.StringProperty \
      (name = "Institution", default = 'Yale University')  
    bpy.types.Scene.lab = bpy.props.StringProperty \
      (name = "Lab", default = 'Tan Lab')  
    bpy.types.Scene.notes = bpy.props.StringProperty \
      (name = "Notes", default = "Intrathecal")  
    bpy.types.Scene.pharmacology = bpy.props.StringProperty \
      (name = "Pharmacology", default = "Romidepsin")
    bpy.types.Scene.protocol = bpy.props.StringProperty \
      (name = "Protocol", default = "AT0003")
    bpy.types.Scene.session_start_time = bpy.props.StringProperty \
      (name = "Session Start Time", default = "2022-12-15 14:35:15") 
    bpy.types.Scene.session_description = bpy.props.StringProperty \
      (name = "Session Description", default = "Image stacks of neurons were converted into OBJs, traced in Tilt Brush, and then segmented in Blender.")
    bpy.types.Scene.slices = bpy.props.StringProperty \
      (name = "Slices", default = "Coronal")
    bpy.types.Scene.surgery = bpy.props.StringProperty \
      (name = "Surgery", default = "Contusion")

    #Imaging Plane Fields
    bpy.types.Scene.plane_name = bpy.props.StringProperty \
      (name = "Plane Name", default = "488nm GFP CF40")
    bpy.types.Scene.plane_description = bpy.props.StringProperty \
      (name = "Plane Description", default = "Plane for GFP")
    bpy.types.Scene.excitation_lambda = bpy.props.FloatProperty \
      (name = "Excitation Lambda", default = 488)
    bpy.types.Scene.external_file = bpy.props.StringProperty \
      (name = "External File Link", default = "https://yalesecure.app.box.com/folder/184104062698")
    bpy.types.Scene.imaging_rate = bpy.props.FloatProperty \
      (name = "Imaging Rate")
    bpy.types.Scene.indicator = bpy.props.StringProperty \
      (name = "Indicator", default = "YFP")
    bpy.types.Scene.location = bpy.props.StringProperty \
      (name = "Location", default = "spinal cord")
    bpy.types.Scene.grid_spacing = bpy.props.FloatProperty \
      (name = "Grid Spacing") 
    bpy.types.Scene.grid_spacing_unit = bpy.props.StringProperty \
      (name = "Grid Spacing Units", default = 'um')
    #Fields that would do better in a dropdown
    bpy.types.Scene.device = bpy.props.StringProperty \
      (name = "Device", default = "iXon EMCCD 1")
    bpy.types.Scene.optical_channel_name = bpy.props.StringProperty \
      (name = "Optical Channel Name", default = "Green")
    bpy.types.Scene.optical_channel_description = bpy.props.StringProperty \
      (name = "Optical Channel Description", default = "Channel for YFP")
    bpy.types.Scene.emission_lambda = bpy.props.FloatProperty \
      (name = "emission_lambda", default = 525)

#Unregister classes so that they don't clash with other addons
def unregister():
    #main panel
    bpy.utils.unregister_class(NeuronAnalysis)

    #operators
    bpy.utils.unregister_class(ExplodingBits)
    bpy.utils.unregister_class(SpinesToCollections)
    bpy.utils.unregister_class(BoundingBoxes)
    bpy.utils.unregister_class(AutoSegmenter)
    bpy.utils.unregister_class(DiscSegmenter)
    bpy.utils.unregister_class(ManualLength)
    bpy.utils.unregister_class(ManualMerge)
    bpy.utils.unregister_class(WriteNWB)

    #Subject fields
    bpy.types.Scene.subject_id
    bpy.types.Scene.age
    #bpy.types.Scene.subject_description
    bpy.types.Scene.sex
    bpy.types.Scene.species
    bpy.types.Scene.strain
    
    #NWBFile fields
    bpy.types.Scene.experiment_description
    bpy.types.Scene.experimenter
    bpy.types.Scene.identifier
    bpy.types.Scene.institution
    bpy.types.Scene.lab
    bpy.types.Scene.notes
    bpy.types.Scene.pharmacology
    bpy.types.Scene.protocol
    bpy.types.Scene.session_start_time
    bpy.types.Scene.session_description
    bpy.types.Scene.slices
    bpy.types.Scene.surgery

    #Imaging plane fields
    bpy.types.Scene.plane_name
    bpy.types.Scene.plane_description
    bpy.types.Scene.excitation_lambda
    bpy.types.Scene.external_file
    bpy.types.Scene.imaging_rate
    bpy.types.Scene.indicator
    bpy.types.Scene.location
    bpy.types.Scene.grid_spacing
    bpy.types.Scene.grid_spacing_unit
    bpy.types.Scene.optical_channel_name
    bpy.types.Scene.optical_channel_description
    bpy.types.Scene.emission_lambda



#Used for importing dropdown menu pieces in a pretty way
# from bpy.types import Panel, PropertyGroup, Scene, WindowManager
# from bpy.props import (
#     IntProperty,
#     EnumProperty,
#     StringProperty,
#     PointerProperty,
# )

