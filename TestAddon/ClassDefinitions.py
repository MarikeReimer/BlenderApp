import bpy
import bmesh
import os
import numpy as np 
from datetime import datetime

#The new way of adding python libraries
import sys
#Replace this path when setting up 
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

        #Add button that separates meshes        
        row = layout.row()
        row.operator('object.exploding_bits', text = 'Separate Meshes')

        #Add button that moves spines to folders
        row = layout.row()
        row.operator('object.spines_to_collections', text = 'Move to Collections')

        #Add button that creates bounding boxes around meshes
        row = layout.row()
        row.operator('object.bounding_boxes', text = 'Add Bounding Box')

        #Add button that adds a length vector to a mesh
        row = layout.row()
        row.operator('object.length_vector', text = 'Draw Length Vector')

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
        return {'FINISHED'}

class SpinesToCollections(bpy.types.Operator):
    bl_idname = 'object.spines_to_collections' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Spines To Collections'
    
    def execute(self, context):
        #Select active objects
        selected_objects = bpy.context.selected_objects
        #Remove them from their current collection
        bpy.ops.collection.objects_remove_all()
        # Loop through all spines, put them in collections 
        for spine in selected_objects:
            #Name the collection after the spine
            collection_name = spine.name
            #Create Collections and link spines to them
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
            collection.objects.link(spine)
        return {'FINISHED'} 

class BoundingBoxes(bpy.types.Operator):
    bl_idname = 'object.bounding_boxes' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Bounding Boxes'
    
    def execute(self, context):
        #Select objects
        selected = bpy.context.selected_objects

        for obj in selected:
            #ensure origin is centered on bounding box center
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            #create a cube for the bounding box
            bpy.ops.mesh.primitive_cube_add() 
            #our new cube is now the active object, so we can keep track of it in a variable:
            bound_box = bpy.context.active_object 

            #copy transforms
            bound_box.dimensions = obj.dimensions
            bound_box.location = obj.location
            bound_box.rotation_euler = obj.rotation_euler

        return {'FINISHED'}

class LengthVector(bpy.types.Operator):
    bl_idname = 'object.length_vector' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Length Vector'

    def execute(self, context):
        # Keep track of current mode
        mode = bpy.context.active_object.mode
        #Set to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Get the currently select object
        obj = bpy.context.object
      
        # Create a numpy array with empty values for each vertex
        sel = np.zeros(len(obj.data.vertices), dtype=np.bool)
        
        # Populate the array with True/False if the vertex is selected
        obj.data.vertices.foreach_get('select', sel)
        
        # Get selected vertex
        for i in np.where(sel==True)[0]:
            # Loop over each currently selected vertex
            v = obj.data.vertices[i]
           
            #For now we will just use the first vertex, but future iteratations could make raycasts from a selection of multiple

        selected_vertex = [v.co[0], v.co[1], v.co[2]]     
        selected_vertex_vector_origin = Vector(selected_vertex)         
        
        #Get center of mass
        center_of_mass = obj.matrix_world.translation

        #Extract XYZ coordinates 
        center_of_mass = [center_of_mass[0], center_of_mass[1], center_of_mass[2]]
        center_of_mass_vector_destination = Vector(center_of_mass)

        #Create a vector between the vertex and the selected mesh's center of mass
        vector_to_center = Vector(center_of_mass_vector_destination - selected_vertex_vector_origin)  
        print(vector_to_center)
            #Raycast using the vector with the mesh's center of mass as its origin
            #Create second vector using the selected vertex and the "hit" from the Raycast

        cast_result = obj.ray_cast(selected_vertex_vector_origin, vector_to_center)
                
        #Extract coordinates from cast_result
        spine_tip = Vector(cast_result[1])

        verts = [selected_vertex_vector_origin, spine_tip] 


        #Get the collection for the origionally selected object     
        collection = obj.users_collection[0]
        print(collection)

        mesh = bpy.data.meshes.new("lengthvector_" + collection.name)  # add the new mesh
        new_mesh = bpy.data.objects.new(mesh.name, mesh)

        collection.objects.link(new_mesh)
        bpy.context.view_layer.objects.active = new_mesh
        
        edges = []
        faces = []

        mesh.from_pydata(verts, edges, faces)

        # Go back to the previous mode
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}




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
              
        #This code extracts the coordinates from vertices in scene collection.  
        #Faces from mesh
        faces = []
        #Vertices from mesh
        mesh_verts = []

        #This loop iterates through all collections and extracts data about the meshes.
        #Todo: It should only create an image segmentation if it is the highest level of collection
        for collection in bpy.data.collections:
            #Create processing module
            module = nwbfile.create_processing_module(collection.name, 'contains processed neuromorphology data from Blender')
            #Create image segmentation
            image_segmentation = ImageSegmentation()
            #Add the image segmentation to the module
            module.add(image_segmentation)
            
            for i in collection.objects:
            #for i in bpy.context.scene.objects:
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
                        image_mask=np.ones((4,4)), #What's the point of this line?
                        faces=faces,
                        vertices=vertices,
                        volume=volume,
                    )

                    
                    bm.free()
                    #Clear lists for next loop
                    faces = []
                    mesh_verts = []      


        os.chdir('C:/Users/meowm/Downloads') #<to do> How do I handle this for the final version?
        #Write the NWB file
        with NWBHDF5IO(nwbfile_name, 'w') as io:
            io.write(nwbfile)

        return {'FINISHED'}