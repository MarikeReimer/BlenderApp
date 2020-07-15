import bpy
import os #todo - add to autoinstaller
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO, image
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
        #Extract subject table strings
        subject_id = bpy.context.scene.subject_id 
        age = bpy.context.scene.age
        subject_description = bpy.context.scene.subject_description
        genotype = bpy.context.scene.genotype
        sex = bpy.context.scene.sex
        species = bpy.context.scene.species
        #Extract NWBfile Strings
        identifier = bpy.context.scene.identifier
        #session_start_time = datetime(bpy.context.scene.session_start_time.tolist())  #Will need to do int fields to get this working
        session_description = bpy.context.scene.session_description
        #Experimenter????

        #Extract Imaging Plane Strings
        plane_name = bpy.context.scene.plane_name
        plane_description = bpy.context.scene.plane_description
        excitation_lambda = float(bpy.context.scene.excitation_lambda)
        imaging_rate = float(bpy.context.scene.imaging_rate)
        indicator = bpy.context.scene.indicator
        location = bpy.context.scene.location
        indicator = bpy.context.scene.indicator
        grid_spacing_unit = bpy.context.scene.grid_spacing_unit

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
        
        #Retrieve strings and floats stored in optical channel properties
        optical_channel_name = bpy.types.Scene.optical_channel_name[1].get('name')
        optical_channel_description = bpy.types.Scene.optical_channel_description[1].get('name')
        emission_lambda = float(bpy.types.Scene.emission_lambda[1].get('default'))
        
        #Create optical channel
        optical_channel = OpticalChannel(
            optical_channel_name,
            optical_channel_description,
            emission_lambda)

        #Create imaging plane
        imaging_plane = nwbfile.create_imaging_plane(
            plane_name, 
            optical_channel, 
            plane_description, 
            device, 
            excitation_lambda, 
            imaging_rate, 
            indicator, 
            location, 
            grid_spacing= [1,1,1], 
            grid_spacing_unit = grid_spacing_unit)

        #Create image series and add a link to the raw image stack to the file
        raw_data = image.ImageSeries(
            'Raw Data',
            format = 'external',
            rate = imaging_rate, #Unit is Hz
            external_file = ['raw_data_link'], #<to do> Remove hard coding
            starting_frame = [1])

        nwbfile.add_acquisition(raw_data)

        #Create processing module
        module = nwbfile.create_processing_module('Blender Data', 'contains processed neuromorphology data from Blender')
        
        #Create image segmentation
        image_segmentation = ImageSegmentation()

        #Add the image segmentation to the module
        module.add(image_segmentation)

        #Create plane segmentation
        plane_segmentation = image_segmentation.create_plane_segmentation('output from segmenting a mesh in Blender',
                                       imaging_plane, 'mesh_segmentaton', raw_data) #<to do> mesh segmentaton should be replaced by name of mesh object

        #Extract data from Blender before passing to ROI columns
        obj = bpy.context.active_object

        bpy.ops.object.origin_set(type = 'ORIGIN_CENTER_OF_MASS')
        center_of_mass = obj.location

        #Extract XYZ coordinates 
        center_of_mass = [center_of_mass[0], center_of_mass[1], center_of_mass[2]]

        plane_segmentation.add_column('volume', 'volume of mesh in X units')
        plane_segmentation.add_column('center_of_mass', 'center of mass of mesh')


        volume = 2 #<to do> replace with volume

        pix_mask1 = [(1,1,2)] #<to do> replace with xyz of vertex points

        plane_segmentation.add_roi(pixel_mask = pix_mask1, volume = volume, center_of_mass = center_of_mass)

        #
        os.chdir('C:/Users/Mrika/Downloads')
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
        wavelength = 300.1 #The emission wavelength for the red channel      

        bpy.types.Scene.optical_channel_name = bpy.props.StringProperty \
        (name = "Red Channel")
        bpy.types.Scene.optical_channel_description = bpy.props.StringProperty \
        (name = "Description of Red Channel")
        bpy.types.Scene.emission_lambda = bpy.props.FloatProperty \
        (default = wavelength)

        print(bpy.types.Scene.optical_channel_name)

        return {'FINISHED'}
   
class GreenOpticalChannel(bpy.types.Operator):
    bl_idname = 'object.green_optical_channel' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'GreenOpticalChannel'

    def execute(self, context):
        wavelength = 500 #The emission wavelength for the green channel 
        
        #Keeping the property group code here in case it's needed later.  Was not able to access my_item outside this class       
        #Use the add() functionality to update OpticalChannelGroup values
        # my_item = bpy.context.scene.my_settings.add()
        # my_item.optical_channel_name = "Green"
        # my_item.optical_channel_description = "The Green channel"
        # my_item.emission_lambda = wavelength

        # print(my_item.optical_channel_name)
        # print(my_item.optical_channel_description)
        # print(my_item.emission_lambda)
        bpy.types.Scene.optical_channel_name = bpy.props.StringProperty \
        (name = "Green Channel")
        bpy.types.Scene.optical_channel_description = bpy.props.StringProperty \
        (name = "Description of Green Channel")
        bpy.types.Scene.emission_lambda = bpy.props.FloatProperty \
        (default = wavelength)

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


#Keeping this here just in case it's needed later
# class OpticalChannelGroup(bpy.types.PropertyGroup):
#     #Property groups use an annotation ':' instead of an '='
#     optical_channel_name : bpy.props.StringProperty()
#     optical_channel_description : bpy.props.StringProperty()
#     emission_lambda : bpy.props.FloatProperty()

# bpy.utils.register_class(OpticalChannelGroup)
# #Associate the OpticalChannelGroup fields with the Scene in an object called 'my_settings"
# bpy.types.Scene.my_settings = bpy.props.CollectionProperty(type = OpticalChannelGroup)
