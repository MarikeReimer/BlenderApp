import bpy
import bmesh
import os
import numpy as np #Delete - only used for testing
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO, image, load_namespaces, get_class
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, ImagingPlane
from pynwb.file import Subject
from pynwb.device import Device
from datetime import datetime
from mathutils import Vector
 
#Load NWB extension for meshes
load_namespaces('MeshClasses.namespace.yaml')
MeshSurface = get_class('MeshAttributes', 'TanLab')
MeshPlaneSegmentation = get_class('MeshPlaneSegmentation', 'TanLab')

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
        print('writing file at', datetime.now())
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
            indicator, 
            location, 
            imaging_rate, 
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
        
        #This code extracts the coordinates from vertices in scene collection.  
        #Vertices from single points/ROIs used to calculate length
        vert_list = [] 
        #Faces from mesh
        faces = []
        #Vertices from mesh
        mesh_verts = []

        #Vert loop
        for i in bpy.context.scene.objects:
            if i.type == 'MESH' and len(i.data.vertices) == 1:
                print(i.name, i.type, 'entering vert loop', datetime.now())
                # Get the active mesh
                mesh = i.data

                # Get a BMesh representation
                #<to do> refactor: define this function outside the loop since I use it more than once
                bm = bmesh.new()
                #Fill Bmesh with the mesh data from the object  
                bm.from_mesh(mesh)
                for v in bm.verts:
                    print("vert coordinates", v.co)
                    vert_list.append(v.co)
               

        #Extract coordinates of the Verts
        #The mesh loop breaks the Vert list, so it lives here 
        point1 = vert_list[0]
        x1 = point1[0]
        y1 = point1[1]
        z1 = point1[2]

        point2 = vert_list[1]
        x2 = point2[0]
        y2 = point2[1]
        z2 = point2[2]

        length = (point1 - point2).length
        print('length', length)


        #Mesh loop
        for i in bpy.context.scene.objects:
            if i.type == 'MESH' and len(i.data.vertices) > 1:
                print(i.name, i.type, 'entering volume loop')
                
                #CENTER OF MASS
                center_of_mass = i.matrix_world.translation

                #Extract XYZ coordinates 
                center_of_mass = [center_of_mass[0], center_of_mass[1], center_of_mass[2]]
            
                #Get mesh data from the active object in the Scene Collection
                mesh = i.data

                #Create an empty BMesh
                bm = bmesh.new()
                #Fill Bmesh with the mesh data from the object  
                bm.from_mesh(mesh)

                volume = bm.calc_volume(signed=False)


                #SURFACE AREA
                surface_area = sum(i.calc_area() for i in bm.faces)
                
                #Add variables to mesh_surface NWB extension

                for v in bm.verts:
                    mesh_verts.append(v.co)
               
                for face in mesh.polygons:
                    vertices = face.vertices
                    face_vert_list = [vertices[0], vertices[1], vertices[2]]
                    faces.append(face_vert_list)

                
                mesh_verts = np.array(mesh_verts)
                print(mesh_verts)

                mesh_surface = MeshSurface(vertices=mesh_verts,
                    volume = volume,
                    faces = faces,
                    center_of_mass = center_of_mass,
                    surface_area = surface_area,
                    name = i.name)
                
                #Create unique name
                segmentation_name = i.name + ' mesh plane_segmentaton'

                #Create plane segmentation from our NWB extension    
                mesh_plane_segmentation = MeshPlaneSegmentation('output from segmenting a mesh in Blender',
                                       imaging_plane, mesh_surface, segmentation_name, raw_data)

                image_segmentation.add_plane_segmentation(mesh_plane_segmentation) 

                #Add column to mesh plane segmentation to store Length. <to do> This should live in the loop 
                mesh_plane_segmentation.add_column('length', 'difference between two Verts')
                
                bm.free()      



        pix_mask1 = [(x1,y1,z1)] 

        mesh_plane_segmentation.add_roi(pixel_mask = pix_mask1, length = length)

        pix_mask2 = [(x2,y2,z2)] 
        mesh_plane_segmentation.add_roi(pixel_mask = pix_mask2, length = length)

        #
        os.chdir('C:/Users/meowm/Downloads') #<to do> How do I handle this for the final version?
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
