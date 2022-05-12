import bpy
import bmesh
import os
import numpy as np #Delete - only used for testing
from datetime import datetime

#The new way of adding python libraries
import sys
#Replace this path
#packages_path = "C:\\Users\\meowm\\AppData\\Roaming\\Python\\Python39\\site-packages"
packages_path = "C:\\Users\\meowm\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages"
sys.path.insert(0, packages_path )

from pynwb import NWBFile, NWBHDF5IO, image
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, ImagingPlane
from pynwb.file import Subject
from pynwb.device import Device
from datetime import datetime
from mathutils import Vector

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

        #Add Device menu (someday):
        row.prop(context.scene, "device")
    
        #Add OpticalChannel menu (someday):
        row.prop(context.scene, "optical_channel_name")
        row.prop(context.scene, "optical_channel_description")
        row.prop(context.scene, "emission_lambda")

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

#Add functionality to dropdowns
#https://blender.stackexchange.com/questions/170219/python-panel-dropdownlist-and-integer-button
# class PlaceholderProperties(PropertyGroup):
#     dropdown_box: EnumProperty(
#         items=(
#             ("A", "Ahh", "Tooltip for A"),
#             ("B", "Be", "Tooltip for B"),
#             ("C", "Ce", "Tooltip for C"),
#         ),
#         name="Description for the Elements",
#         default="A",
#         description="Tooltip for the Dropdownbox",
#     )


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
        #session_start_time = datetime(bpy.context.scene.session_start_time.tolist())  #Should read this from meta data.
        session_description = bpy.context.scene.session_description
        #Experimenter???? shroos forgot this field

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

        #Extract Strings Which Belong in Dropdown Menus
        plane_name = bpy.context.scene.plane_name
        device = bpy.context.scene.device
        optical_channel_name = bpy.context.scene.optical_channel_name
        optical_channel_description = bpy.context.scene.optical_channel_description
        emission_lambda = bpy.context.scene.emission_lambda

        #Add selected device        
        device = nwbfile.create_device(name = device)
 
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
            grid_spacing= [1,1,1], #shouldn't be hardcoded
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
        #Faces from mesh
        faces = []
        #Vertices from mesh
        mesh_verts = []

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
             
                #Create unique name
                segmentation_name = i.name + ' mesh plane_segmentaton'

                #Create plane segmentation from our NWB extension    
                plane_segmentation = image_segmentation.create_plane_segmentation(
                    name = segmentation_name,
                    description = 'output from segmenting a mesh in Blender',
                    imaging_plane = imaging_plane,     
                    reference_images = raw_data
                )                       


                #Add column to mesh plane segmentation to store Length. <to do> This should live in the loop 
                #plane_segmentation.add_column('length', 'difference between two Verts')
                plane_segmentation.add_column('faces', 'faces of mesh', index=True)
                plane_segmentation.add_column('vertices', 'vertices of mesh', index=True)
                plane_segmentation.add_column('volume', 'volume')

                plane_segmentation.add_roi(
                    image_mask=np.ones((4,4)),
                    faces=faces,
                    vertices=vertices,
                    volume=volume,
                )

                
                bm.free()      


        os.chdir('C:/Users/meowm/Downloads') #<to do> How do I handle this for the final version?
        #Write the NWB file
        with NWBHDF5IO(nwbfile_name, 'w') as io:
            io.write(nwbfile)

        return {'FINISHED'}