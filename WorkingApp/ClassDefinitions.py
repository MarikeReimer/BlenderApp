import bpy
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation
from pynwb.file import Subject
from pynwb.device import Device

#NeuronAnalysis creates a 3Dview panel and add rows for fields and buttons. 
#Blender's documentation describes what the strings that start with "bl_" do: https://docs.blender.org/api/blender_python_api_2_70_5/bpy.types.Panel.html#bpy.types.Panel.bl_idname

class NeuronAnalysis(bpy.types.Panel):
    bl_label = "Neuron Analysis" #The name of our panel
    bl_idname = "PT_TestPanel" #Gives the panel gets a custom ID, otherwise it takes the name of the class used to define the panel.  Used default from template
    bl_space_type = 'VIEW_3D' #Puts the panel on the VIEW_3D tool bar
    bl_region_type = 'UI' #The region where the panel will be used
    bl_category = 'NeuronAnalysis' #The category is used for filtering in the add-ons panel.
    
    #Create a layout and add fields and buttons to it
    def draw(self, context):
        layout = self.layout
        #Add button that separates dendrites        
        row = layout.row()
        row.operator('object.exploding_bits', text = 'Separate Dendrites')
        
        #Add Device menu:
        row = layout.row()
        row.menu(DeviceMenu.bl_idname, text = 'Microscope Selector')

        row = layout.row()
        #Add button that writes data from panel and object values to an NWB file
        row.operator('object.write_nwb', text = "Write NWB File")
        row = self.layout.column(align = True)
        #Add fields for the Subject class strings
        row.prop(context.scene, "subject_id")
        row.prop(context.scene, "age")
        row.prop(context.scene, "subject_description")
        row.prop(context.scene, "genotype")
        row.prop(context.scene, "sex")
        row.prop(context.scene, "species")
        #Add fields for NWBFile strings
        row.prop(context.scene, "identifier")
        row.prop(context.scene, "session_start_time")
        row.prop(context.scene, "session_description")
        
#Row Operators

#Row operator for that applies "separate by loose parts" to mesh    
class ExplodingBits(bpy.types.Operator):
    bl_idname = 'object.exploding_bits' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Exploding Bits'
    
    def execute(self, context):
        #Select active object
        object = bpy.context.active_object
        #Split it into pieces
        bpy.ops.mesh.separate(type='LOOSE')
        return {'FINISHED'} #Todo - explain why this is needed


#Row operator for writing  data toNWB file
class WriteNWB(bpy.types.Operator):
    bl_idname = 'object.write_nwb' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Write NWB File'

    #Extract data from panel and object
    def execute(self, context):
        #Extract strings
        subject_id = bpy.context.scene.subject_id 
        age = bpy.context.scene.age
        subject_description = bpy.context.scene.subject_description
        genotype = bpy.context.scene.genotype
        sex = bpy.context.scene.sex
        species = bpy.context.scene.species
        identifier = bpy.context.scene.identifier
        #session_start_time = datetime(bpy.context.scene.session_start_time.tolist())  #Will need to do string manipulations of some sort to get this working
        session_description = bpy.context.scene.session_description

        #Create filename 
        nwbfile_name = identifier + '.nwb'

        #Create pynwb subject
        subject = Subject(
            description = subject_description,
            genotype = genotype,
            sex = sex,
            species = species,
            subject_id = subject_id
            )

        #Create pywnb File
        nwbfile = NWBFile(session_description = session_description,
            identifier = identifier, 
            session_start_time = datetime.now(),  #Fix this
            file_create_date = datetime.now(),
            subject = subject
            )  

        nwbfile.add_device(device)

        #Write the NWB file
        with NWBHDF5IO(nwbfile_name, 'w') as io:
            io.write(nwbfile)

        return {'FINISHED'}

#Row operator for selecting widefield as the device used
class WideField(bpy.types.Operator):
    bl_idname = 'object.wide_field' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Wide_field'
    def execute(self, context):
        device = Device('Wide_field')
        print(device)
        return {'FINISHED'}
    

#Row operator for selecting 2P as the device used
class TwoPhoton(bpy.types.Operator):
    bl_idname = 'object.two_photon' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'TwoPhoton'
    def execute(self, context):
        device = Device('Two Photon')
        print(device)
        return {'FINISHED'}



#Menus
class DeviceMenu(bpy.types.Menu):
    bl_label = "Device Menu"
    bl_idname = "OBJECT_MT_device_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.two_photon")
        layout.operator("object.wide_field")