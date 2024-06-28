from email.policy import default
import bpy
from datetime import datetime

#Import class definitions
from . ClassDefinitions import NeuronAnalysis
from . ClassDefinitions import ExplodingBits
from . ClassDefinitions import ManualLength
from . ClassDefinitions import WriteNWB
from . ClassDefinitions import SpineSlicer
from . ClassDefinitions import SegmentHollowSpines
from . ClassDefinitions import LoadDataJoint
from . ClassDefinitions import FILE_SELECT_OT_SelectFile
from . ClassDefinitions import SelectDirectoryOperator

#Information about the Addon created by the Blender Development VSCode Extension
bl_info = {
    "name" : "VRSASEAddon",
    "author" : "Marike Reimer",
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
    bpy.utils.register_class(SpineSlicer)
    bpy.utils.register_class(SegmentHollowSpines)
    bpy.utils.register_class(ManualLength)
    bpy.utils.register_class(WriteNWB)

    bpy.utils.register_class(LoadDataJoint)
    # bpy.utils.register_class(DropCurrentSubjectIdentifier)
    bpy.utils.register_class(FILE_SELECT_OT_SelectFile)
    bpy.utils.register_class(SelectDirectoryOperator)
 
       
    #Subject Table fields
    bpy.types.Scene.subject_id = bpy.props.StringProperty \
      (name = "Subject ID", default = "L")
    bpy.types.Scene.age = bpy.props.StringProperty \
      (name = "Age", default = "P14W")
    bpy.types.Scene.subject_description = bpy.props.StringProperty \
      (name = "Description", default = '')
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
      (name = "Experiment Description", default = 'We developed a dendritic spine analysis platform using virtual reality and Blender to study the efficacy of romidepsin as a treatment to reduce spasticity and abnormal dendritic spine growth following a spinal cord contusion injury.')    
    bpy.types.Scene.experimenter = bpy.props.StringProperty \
      (name = "Experimenter", default = "")
    bpy.types.Scene.identifier = bpy.props.StringProperty \
      (name = "Identifier", default = 'Neuron#_Dendrite#')
    bpy.types.Scene.institution = bpy.props.StringProperty \
      (name = "Institution", default = 'Yale University')  
    bpy.types.Scene.lab = bpy.props.StringProperty \
      (name = "Lab", default = '')  
    bpy.types.Scene.notes = bpy.props.StringProperty \
      (name = "Notes", default = "")  
    bpy.types.Scene.pharmacology = bpy.props.StringProperty \
      (name = "Pharmacology", default = "Romidepsin 2.5mg/kg inject IP 4 weeks after SCI")
    bpy.types.Scene.protocol = bpy.props.StringProperty \
      (name = "Protocol", default = "")
    bpy.types.Scene.session_description = bpy.props.StringProperty \
      (name = "Session Description", default = "Image stacks of neurons were converted into OBJs, traced in Tilt Brush, and then segmented in Blender.")
    bpy.types.Scene.slices = bpy.props.StringProperty \
      (name = "Slices", default = "Coronal")
    bpy.types.Scene.surgery = bpy.props.StringProperty \
      (name = "Surgery", default = "Contusion: (50 kDyn) SCI at the thoracic vertebral level 11 (T11), lumbar segment 2 (L2)")

    #Imaging Plane Fields
    bpy.types.Scene.plane_name = bpy.props.StringProperty \
      (name = "Plane Name", default = "488nm GFP CF40")
    bpy.types.Scene.plane_description = bpy.props.StringProperty \
      (name = "Plane Description", default = "Plane for YFP")
    bpy.types.Scene.excitation_lambda = bpy.props.FloatProperty \
      (name = "Excitation Lambda", default = 488)
    bpy.types.Scene.external_file = bpy.props.StringProperty \
      (name = "External File Link", default = "C:/Users/meowm/OneDrive/TanLab/DataJointTesting/Images")
    bpy.types.Scene.imaging_rate = bpy.props.FloatProperty \
      (name = "Imaging Rate")
    bpy.types.Scene.indicator = bpy.props.StringProperty \
      (name = "Indicator", default = "Thy1-YFP")
    bpy.types.Scene.location = bpy.props.StringProperty \
      (name = "Location", default = "lumbar spinal cord")
    bpy.types.Scene.grid_spacing = bpy.props.FloatProperty \
      (name = "Grid Spacing", default = 8.2982)
    bpy.types.Scene.grid_spacing_unit = bpy.props.StringProperty \
      (name = "Grid Spacing Units", default = 'pixels/micron')
    bpy.types.Scene.device = bpy.props.StringProperty \
      (name = "Device", default = "iXon EMCCD 1")
    bpy.types.Scene.optical_channel_name = bpy.props.StringProperty \
      (name = "Optical Channel Name", default = "Green")
    bpy.types.Scene.optical_channel_description = bpy.props.StringProperty \
      (name = "Optical Channel Description", default = "Channel for YFP")
    bpy.types.Scene.emission_lambda = bpy.props.FloatProperty \
      (name = "emission_lambda", default = 525)     


    # bpy.types.Scene.my_path_property = bpy.props.StringProperty \
    #   (name="Select Output Directory")#, default = "C:\Users\meowm\OneDrive\TanLab\DataJointTesting\NWBfiles")
    bpy.types.Scene.my_path_property = bpy.props.StringProperty \
      (name="Output Directory", subtype='DIR_PATH', default = 'C:/Users/meowm/OneDrive/TanLab/DataJointTesting/NWBFiles') #, subtype='FILE_PATH',  # Use FILE_PATH for file selection
    
    
    #DataJoint Fields
    bpy.types.Scene.selected_file = bpy.props.StringProperty \
      (name="Selected File", default = "C:/Users/meowm/OneDrive/TanLab/DataJointTesting/DataJointDiscDendriteTable_V1.csv")
        
    bpy.types.Scene.host = bpy.props.StringProperty \
      (name = "host", default = "spinup-db001f1f.cluster-cyynsscieqtk.us-east-1.rds.amazonaws.com")
    bpy.types.Scene.datajoint_user = bpy.props.StringProperty \
      (name = "datajoint_user", default = "MarikeReimer")
    bpy.types.Scene.datajoint_password = bpy.props.StringProperty \
      (name = "datajoint_password", default = "uqHKL3YLMCG0")


#Unregister classes so that they don't clash with other addons
def unregister():
    #main panel
    bpy.utils.unregister_class(NeuronAnalysis)

    #operators
    bpy.utils.unregister_class(ExplodingBits)
    bpy.utils.unregister_class(ManualLength)
    bpy.utils.unregister_class(WriteNWB)
    bpy.utils.unregister_class(SpineSlicer)
    bpy.utils.unregister_class(SegmentHollowSpines)
    bpy.utils.unregister_class(FILE_SELECT_OT_SelectFile)
    bpy.utils.unregister_class(SelectDirectoryOperator)
    bpy.utils.unregister_class(LoadDataJoint)
    #bpy.utils.unregister_class(DropCurrentSubjectIdentifier)
    

    #Subject fields
    bpy.types.Scene.subject_id
    bpy.types.Scene.age
    bpy.types.Scene.subject_description
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

    #del bpy.types.Scene.my_path_property
    
    #DataJoint fields
    bpy.types.Scene.selected_file
    bpy.types.Scene.host
    bpy.types.Scene.datajoint_user
    bpy.types.Scene.datajoint_password


#Used for importing dropdown menu pieces in a pretty way
# from bpy.types import Panel, PropertyGroup, Scene, WindowManager
# from bpy.props import (
#     IntProperty,
#     EnumProperty,
#     StringProperty,
#     PointerProperty,
# )