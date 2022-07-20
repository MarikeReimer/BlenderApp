import bpy
import bmesh
import os
import numpy as np 
from datetime import datetime
import math

#The new way of adding python libraries
import sys
#Replace this path when setting up 
packages_path = "C:\\Users\\meowm\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages"
sys.path.insert(0, packages_path )

from pynwb import NWBFile, NWBHDF5IO, image
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, ImagingPlane
from pynwb.file import Subject
from pynwb.device import Device
from mathutils import Vector
from mathutils.bvhtree import BVHTree

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
        row.operator('object.spines_to_collections', text = 'Spines to Collections')

        #Add button that creates bounding boxes around meshes
        row = layout.row()
        row.operator('object.bounding_boxes', text = 'Add Bounding Box')

        #Add button that adds a length vector to a mesh
        row = layout.row()
        row.operator('object.length_vector', text = 'Draw Length Vector')

        #Add button that adds a length vector to a mesh
        row = layout.row()
        row.operator('object.autosegmenter', text = 'Auto-Segment')

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

#Autosgementer
#Select dendrites
#Get all other meshes and put them into a list
#For each mesh in the list
    #Turn it into a BVH Tree
    #Find the indices of overlapping polygon faces
    #Create a new mesh from the centers of the polygon
    #Create a vector called "Spine Base" at the center of the new mesh
    # Measure the distance between Spine Base and all other vertices in the mesh
    #Create Spine Tip at the maximum distance from Spine Base
    #Create a collection named after the mesh, move the original  mesh and the spine_ends into it

class AutoSegmenter(bpy.types.Operator):
    bl_idname = 'object.autosegmenter' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'AutoSegmenter'
    
    def find_intersections(self):
        #Select Dendrite mesh
        dendrite = bpy.context.active_object
        #Create a list of all meshes except for the       
        mesh_list = [ mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH']  
        mesh_list.remove(dendrite)

        #Turn the dendrite into a BVH tree
        dendrite_mesh = bmesh.new()
        dendrite_mesh.from_mesh(bpy.context.scene.objects[dendrite.name].data)
        dendrite_mesh.transform(dendrite.matrix_world)
        dendrite_BVHtree = BVHTree.FromBMesh(dendrite_mesh)

        intersecting_spines = []
        face_centers_list =[]

        #Iterate through the dendrititic spines in the mesh list
            #Find overlapping polygons between spines and dendrite meshes and store them in "face centers"
            #Find the center of the overlapping polygons and store it in "Spine Base"
            #Find overlapping polygons between spines and dendrite meshes and store them in "face centers"
        for spine_mesh in mesh_list:                                   
            BVH_spine_mesh = bmesh.new()
            BVH_spine_mesh.from_mesh(bpy.context.scene.objects[spine_mesh.name].data)
            BVH_spine_mesh.transform(spine_mesh.matrix_world)
            BVH_spine_mesh.faces.ensure_lookup_table() 
            BVHtree_mesh = BVHTree.FromBMesh(BVH_spine_mesh)                        
            overlap = dendrite_BVHtree.overlap(BVHtree_mesh) #overlap is list containing pairs of polygon indices, the first index is a vertex from the dendrite mesh tree the second is from the spine mesh tree
                        
            face_centers = []                      

            overlapping_spine_face_index_list = [pair[1] for pair in overlap]

            if overlapping_spine_face_index_list is not None:
                intersecting_spines.append(BVH_spine_mesh)

            for face_index in overlapping_spine_face_index_list:
                face_data = BVH_spine_mesh.faces[face_index]                
                face_centers.append(face_data.calc_center_median())
            
            face_centers_list.append(face_centers)
            face_centers = []
        
        return(face_centers_list, intersecting_spines)     
    
    def find_midpoints(self):        
        Bob = self.find_intersections() 
        face_centers_list = Bob[0]
        intersecting_spines = Bob[1]
        edges = []
        faces = []
        spine_base_list = []

        for spine_mesh in intersecting_spines:
            print(spine_mesh)
            #Add face centers as vertices:
            face_center_mesh = bpy.data.meshes.new("face centers")  # add the new mesh
            obj = bpy.data.objects.new(face_center_mesh.name, face_center_mesh)
            col = bpy.data.collections.get("Collection")
            col.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            face_centers = face_centers_list[0]
            face_centers_list.remove(face_centers_list[0])
            face_center_mesh.from_pydata(face_centers, edges, faces)

            #Add spine base as Mesh to Blender
            spine_base_mesh = bpy.data.meshes.new("Spine Base")  # add the new mesh
            obj = bpy.data.objects.new(spine_base_mesh.name, spine_base_mesh) 
            col = bpy.data.collections.get("Collection")
            col.objects.link(obj)
            bpy.context.view_layer.objects.active = obj                  
            #Find the center of the overlapping polygons and store it in "Spine Base"
            x, y, z = [ sum( [v.co[i] for v in face_center_mesh.vertices] ) for i in range(3)]
            count = float(len(face_center_mesh.vertices))
            spine_base = Vector( (x, y, z ) ) / count           
            spine_base_coords = [spine_base]
            spine_base_mesh.from_pydata(spine_base_coords, edges, faces)
            spine_base_list.append(spine_base_mesh)
        return(spine_base_list)
    
    def execute(self, context):
        Bob = self.find_intersections() 
        intersecting_spines = Bob[1]
        spine_base_list = self.find_midpoints()
        edges = []
        faces = []
      
        for spine_mesh in intersecting_spines:
            spine_base = spine_base_list[0]
            spine_base = spine_base.vertices[0].co
            #print(spine_base.data.vertices)
            #print(spine_base.verts)
            #print("spine base coordinates", spine_base.vertices[0].co)
            print(spine_base)
            spine_base_list.remove(spine_base_list[0])
            #Compare the distance between Spine Base and all other verticies in spine_mesh and store in "spine_length_dict"   
            spine_length_dict = {}
            spine_coordinates_dict = {}
                                    
            for vert in spine_mesh.verts:
            #for vert in spine_mesh.verts:
                length = math.dist(vert.co, spine_base)         
                spine_length_dict[vert.index] = length
                spine_coordinates_dict[vert.index] = vert.co                

            spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
            spine_tip = spine_coordinates_dict[spine_tip_index]

            #Vectors are the same between dictionary and mesh vertices
            # print("Tip from spine mesh",spine_mesh.data.vertices[spine_tip_index].co)            
            # print("Tip from coordinates dict", spine_coordinates_dict[spine_tip_index])
            # print(spine_length_dict)

            #Clear dictionary between loops    
            spine_length_dict = {}
            spine_coordinates_dict = {}

            #Create a mesh with spine_base and spine_tip
            endpoint_mesh = bpy.data.meshes.new("Base and tip")  # add the new mesh
            obj = bpy.data.objects.new(endpoint_mesh.name, endpoint_mesh)
            col = bpy.data.collections.get("Collection")
            col.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
                    
            verts = [spine_base, spine_tip]
    
            endpoint_mesh.from_pydata(verts, edges, faces)
            print(endpoint_mesh)

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


        #Get the collection for the originally selected object     
        collection = obj.users_collection[0]
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