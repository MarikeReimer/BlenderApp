import bpy
from datetime import datetime
from pynwb import NWBFile
from pynwb import NWBHDF5IO
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, ImagingPlane
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

        #Add Device menu:
        row = layout.row()
        row.menu(DeviceMenu.bl_idname, text = 'Microscope Selector')

        #Add OpticalChannel menu:
        row = layout.row()
        row.menu(OpticalChannelMenu.bl_idname, text = 'Channel Selector')

        #Add fields for Imaging Plane
        row = self.layout.column(align = True)
        row.prop(context.scene, "plane_name")
        row.prop(context.scene, "plane_description")
        row.prop(context.scene, "excitation_lambda")
        row.prop(context.scene, "imaging_rate")
        row.prop(context.scene, "indicator")
        row.prop(context.scene, "location")
        row.prop(context.scene, "grid_spacing")
        row.prop(context.scene, "grid_spacing_unit")


        #Add button that separates dendrites        
        row = layout.row()
        row.operator('object.exploding_bits', text = 'Separate Dendrites')

        #Add button that writes data from panel and object values to an NWB file
        row = layout.row()
        row.operator('object.write_nwb', text = "Write NWB File")


#ROW OPERATORS

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
        #session_start_time = datetime(bpy.context.scene.session_start_time.tolist())  #Will need to do int fields to get this working
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

        #Add selected device
        device_name = bpy.types.Scene.device[1].get('name') #I don't know why the [1] is needed.  Neither did the tutorial: https://ontheothersideofthefirewall.wordpress.com/blender-change-textfield-on-click-of-a-button-dictionaries-and-stringproperty/
        device = nwbfile.create_device(name = device_name)


        # imaging_plane = nwbfile.create_imaging_plane(
        #     plane_name, 
        #     optical_channel, 
        #     plane_description, 
        #     device, 
        #     excitation_lambda, 
        #     imaging_rate, 
        #     indicator, 
        #     location, 
        #     grid_spacing= [1,1,1], 
        #     grid_spacing_unit = grid_spacing_unit)

        #Write the NWB file
        with NWBHDF5IO(nwbfile_name, 'w') as io:
            io.write(nwbfile)

        return {'FINISHED'}

#Row operator for selecting widefield as the device used
#Because of Blender reserves the 'return' function, the way to access strings outside of classes is to store them as String Properties attached to the Scene.  
class WideField(bpy.types.Operator):
    bl_idname = 'object.wide_field' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Wide_field'
    def execute(self, context):
        bpy.types.Scene.device = bpy.types.Scene.wide_field
        return {'FINISHED'}
    

#Row operator for selecting 2P as the device used
class TwoPhoton(bpy.types.Operator):
    bl_idname = 'object.two_photon' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'TwoPhoton'
    def execute(self, context):
        bpy.types.Scene.device = bpy.types.Scene.two_photon
        return {'FINISHED'}

class RedOpticalChannel(bpy.types.Operator):
    bl_idname = 'object.red_optical_channel' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'RedOpticalChannel'
    def execute(self, context):
        red_wavelength = 500
        optical_channel = OpticalChannel(
            name = 'Red channel',
            description = "Red channel",
            emission_lambda = float(red_wavelength)  #Todo - check names and values
        )
        return optical_channel
        return {'FINISHED'}

class GreenOpticalChannel(bpy.types.Operator):
    bl_idname = 'object.green_optical_channel' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'GreenOpticalChannel'
    def execute(self, context):
        green_wavelength = 500
        optical_channel = OpticalChannel(
            name = 'Red channel',
            description = "Red channel",
            emission_lambda = float(green_wavelength)  #Todo - check names and values
        )
        return optical_channel
        return {'FINISHED'}

#MENUS
class DeviceMenu(bpy.types.Menu):
    bl_label = "Device Menu"
    bl_idname = "OBJECT_MT_device_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.two_photon")
        layout.operator("object.wide_field")

class OpticalChannelMenu(bpy.types.Menu):
    bl_label = "Optical Channel Menu"
    bl_idname = "OBJECT_MT_optical_channel_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.red_optical_channel")
        layout.operator("object.green_optical_channel")