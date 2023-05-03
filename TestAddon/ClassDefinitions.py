import bpy
import bmesh
import os
import numpy as np 
from datetime import datetime
import math

#The new way of adding python libraries
import sys
#TODO: Replace this path when setting up 
packages_path = "C:\\Users\\meowm\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages"
sys.path.insert(0, packages_path )

from pynwb import NWBFile, NWBHDF5IO, image
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, ImagingPlane
from pynwb.file import Subject
from pynwb.device import Device
from mathutils import Vector
from mathutils.bvhtree import BVHTree

#NeuronAnalysis creates a 3Dview panel and add rows for text entry fields and buttons linked to operators.

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
        #row.prop(context.scene, "subject_description")
        row.prop(context.scene, "genotype")
        row.prop(context.scene, "sex")
        row.prop(context.scene, "species")
        row.prop(context.scene, "strain")
        #Add fields for NWBFile strings
        row.prop(context.scene, "experimenter")
        row.prop(context.scene, "experiment_description")
        row.prop(context.scene, "identifier")
        row.prop(context.scene, "institution")
        row.prop(context.scene, "lab")
        row.prop(context.scene, "notes")
        row.prop(context.scene, "pharmacology")
        row.prop(context.scene, "protocol")
        row.prop(context.scene, "session_start_time")
        row.prop(context.scene, "session_description")
        row.prop(context.scene, "slices")
        row.prop(context.scene, "surgery")

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
        row.prop(context.scene, "external_file")
        row.prop(context.scene, "imaging_rate")
        row.prop(context.scene, "indicator")
        row.prop(context.scene, "location")
        row.prop(context.scene, "grid_spacing")
        row.prop(context.scene, "grid_spacing_unit")

        #Add button that separates meshes        
        row = layout.row()
        row.operator('object.exploding_bits', text = 'Separate Meshes')
        
        # #Add button that merges fragmented meshes
        # row = layout.row()
        # row.operator('object.manual_merge', text = 'Show Fractured Spines')

        #Add button that moves spines to folders
        # row = layout.row()
        # row.operator('object.spines_to_collections', text = 'Move to Collections')

        #Add button that creates bounding boxes around meshes
        # row = layout.row()
        # row.operator('object.bounding_boxes', text = 'Add Bounding Box')

        #Add button that moves spines to folders and adds a spine base and tip 
        row = layout.row()
        row.operator('object.autosegmenter', text = 'Auto-Segment')

        #Add button that moves spines to folders and adds a spine base and tip
        row = layout.row()
        row.operator('object.discsegmenter', text = 'Disc Method Segment')

        #Add button that adds a spine tip if you select its base
        row = layout.row()
        row.operator('object.individual_length_finder', text = 'Manual Length')    

        #Add button that writes data from panel and object values to an NWB file
        row = layout.row()
        row.operator('object.write_nwb', text = "Write NWB File")

#ROW OPERATORS

#Row operator that applies "separate by loose parts" to mesh    
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
    #Create a new mesh from the center of the polygons
    #Create a vector called "Spine Base" at the center of the new mesh
    #Measure the distance between Spine Base and all other vertices in the mesh
    #Create Spine Tip at the maximum distance from Spine Base
    #Create a collection named after the mesh, move the original mesh and the spine endpoints into it

class AutoSegmenter(bpy.types.Operator): #TODO Remove globals from this class
    bl_idname = 'object.autosegmenter' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'AutoSegmenter'
    
    #Generate a BVH tree from the dendrite to check for intersecting spines
    def dendrite_BVH_tree(self):
        global dendrite_BVHtree
        print("Growing BVHtree")
        #Select Dendrite mesh        
        dendrite = bpy.context.active_object     
    
        #Load the dendrite data into a mesh
        dendrite_mesh = bmesh.new()
        dendrite_mesh.from_mesh(bpy.context.scene.objects[dendrite.name].data)
        dendrite_mesh.transform(dendrite.matrix_world)
        dendrite_BVHtree = BVHTree.FromBMesh(dendrite_mesh)

        dendrite_mesh.free()
        return {'FINISHED'}
        

    def list_meshes(self):
        global mesh_list
        print("finding meshes")
        mesh_list = [ mesh for mesh in bpy.data.objects if mesh.type == 'MESH']

        dendrite = bpy.context.active_object  
        mesh_list.remove(dendrite)

        return {'FINISHED'}
        
    #Iterate through the spines in the mesh list
    #Find overlapping polygons between spines and dendrite meshes and store them in "face centers"
    #Check to see if the spine overlaps 
    def find_intersections(self):
        global intersecting_spines
        global spine_names
        global overlapping_spine_face_index_list
        overlapping_spine_face_index_list = []
        intersecting_spines = []
        spine_names = []
        print("finding intersections")

        for spine_mesh in mesh_list:                                 
            BVH_spine_mesh = bmesh.new()
            BVH_spine_mesh.from_mesh(bpy.context.scene.objects[spine_mesh.name].data)
            BVH_spine_mesh.transform(spine_mesh.matrix_world)
            BVH_spine_mesh.faces.ensure_lookup_table() 
            BVHtree_mesh = BVHTree.FromBMesh(BVH_spine_mesh)                        
            overlap = dendrite_BVHtree.overlap(BVHtree_mesh) #overlap is list containing pairs of polygon indices, the first index is a vertex from the dendrite mesh tree the second is from the spine mesh tree
            overlapping_spine_face_index_list_local = [pair[1] for pair in overlap]
            
            #Check to see if the spines overlap the dendrite before passing them to the BVH spine mesh list.  If not, restart the loop.  This filters out disconnected spines

            if overlapping_spine_face_index_list_local:
                overlapping_spine_face_index_list.append(overlapping_spine_face_index_list_local)
                intersecting_spines.append(BVH_spine_mesh)
                spine_names.append(spine_mesh.name)
            else:
                pass
        
        return {'FINISHED'}

    def spines_to_collections(self):
        print("moving spines to folders")
        #Add spines to their own folders
        for spine_mesh in mesh_list:
            old_collection_name = spine_mesh.users_collection
            old_collection_name = old_collection_name[0]
            old_collection_name.objects.unlink(spine_mesh)

            new_collection_name = spine_mesh.name
            new_collection = bpy.data.collections.new(new_collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            new_collection.objects.link(spine_mesh)
        return {'FINISHED'}

    def find_intersecting_face_centers(self):
        print("finding intersections")
        global face_centers_list
        face_centers_list = []
        counter = 0

        for BVH_spine_mesh in intersecting_spines:
            face_centers = []
            
            #Make a collection of points in the faces of intersecting faces    
            for face_index in overlapping_spine_face_index_list[counter]:
                face_data = BVH_spine_mesh.faces[face_index]                
                face_centers.append(face_data.calc_center_median())
            
            counter += 1
            face_centers_list.append(face_centers)
            face_centers = []

        
        return(face_centers_list, intersecting_spines)     
    
    def find_spine_base(self):
        global spine_base_list
        spine_base_list = []
        print("finding base")      
        edges = []
        faces = []
        counter = 0

        for spine_mesh in intersecting_spines:
            #Add face centers as vertices:
            face_center_mesh = bpy.data.meshes.new("face centers")  # add the new mesh
            obj = bpy.data.objects.new(face_center_mesh.name, face_center_mesh)
            col = bpy.data.collections.get("Collection")
            # col.objects.link(obj)
            # bpy.context.view_layer.objects.active = obj
                        
            face_centers = face_centers_list[counter]

            counter += 1
            
            face_center_mesh.from_pydata(face_centers, edges, faces)

            #Add spine base as Mesh to Blender
            spine_base_mesh = bpy.data.meshes.new("Spine Base")  # add the new mesh
            obj = bpy.data.objects.new(spine_base_mesh.name, spine_base_mesh) 

            #Find the center of the overlapping polygons and store it in "Spine Base"
            x, y, z = [ sum( [v.co[i] for v in face_center_mesh.vertices] ) for i in range(3)] #Tested: This does need to be 3
            count = float(len(face_center_mesh.vertices))
            spine_base = Vector( (x, y, z ) ) / count        
            spine_base_coords = [spine_base]
            spine_base_mesh.from_pydata(spine_base_coords, edges, faces)
            spine_base_list.append(spine_base_mesh)

        return(spine_base_list, intersecting_spines)
    
    def find_spine_tip(self):
        print("finding tip")
        global spine_tip_list
        spine_tip_list = []

        for spine_mesh in intersecting_spines:
            counter = 0
            spine_base = spine_base_list[counter]
            counter += 1
            spine_base = spine_base.vertices[0].co
            spine_length_dict = {}
            spine_coordinates_dict = {}
                                    
            for vert in spine_mesh.verts:
                length = math.dist(vert.co, spine_base)         
                spine_length_dict[vert.index] = length
                spine_coordinates_dict[vert.index] = vert.co                

            spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
            spine_tip = spine_coordinates_dict[spine_tip_index]
            spine_tip_list.append(spine_tip)

        return(spine_tip_list)

    def create_base_and_tip(self):
        print("creating base and tip")
        edges = []
        faces = []
        counter = 0
        
        for spine_mesh in intersecting_spines:
            #remove mesh from collection
            spine_base = spine_base_list[counter]            
            spine_tip = spine_tip_list[counter]
            spine_name = spine_names[counter]
            spine_base = spine_base.vertices[0].co

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

            #Clear dictionary between loops    
            spine_length_dict = {}
            spine_coordinates_dict = {}

            #Create a mesh with spine_base and spine_tip
           
            endpoint_mesh = bpy.data.meshes.new(spine_name)  # add the new mesh
            endpoint_mesh_name = "endpoints_" + str(spine_name)
            obj = bpy.data.objects.new(endpoint_mesh_name, endpoint_mesh)

            #Put the endpoint mesh into the same folder as its spine
            collection = bpy.context.scene.collection.children.get(spine_name)
            collection.objects.link(obj)
                                
            verts = [spine_base, spine_tip]
    
            endpoint_mesh.from_pydata(verts, edges, faces)
            counter += 1

        return {'FINISHED'}          
    
    def execute(self, context):
        print("entering execute")
        self.dendrite_BVH_tree()
        self.list_meshes()
        self.find_intersections()
        self.spines_to_collections()
        self.find_intersecting_face_centers()
        self.find_spine_base()
        self.find_spine_tip()
        self.create_base_and_tip()
        return {'FINISHED'}

#Discsegmenter as above, but for discs.  Uses verticies instead of polygons
#Select dendrites
#Get all other meshes and put them into a list
#For each mesh in the list
    #Turn it into a BVH Tree
    #Find the indices of overlapping polygon faces
    #Create a new mesh from the center of the polygons
    #Create a vector called "Spine Base" at the center of the new mesh
    #Measure the distance between Spine Base and all other vertices in the mesh
    #Create Spine Tip at the maximum distance from Spine Base
    #Create a collection named after the mesh, move the original mesh and the spine endpoints into it

class DiscSegmenter(bpy.types.Operator): #TODO Remove globals from this class
    bl_idname = 'object.discsegmenter' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'AutoSegmenter'
    
    #Get Spines
    def get_spines(self):  
        #spine_list = [mesh for mesh in bpy.context.selected_objects if mesh.type == 'MESH']
        spine_list = [mesh for mesh in bpy.context.selected_objects]
        
        all_obs = [ mesh for mesh in bpy.data.objects]
        slicer_list = []

        for obj in all_obs:
            if obj not in spine_list:
                slicer_list.append(obj)

        return(spine_list, slicer_list)
        
    def spines_to_collections(self, spine_list):
        print("moving spines to folders")
        #Add spines to their own folders
        for spine_mesh in spine_list:
            old_collection_name = spine_mesh.users_collection
            old_collection_name = old_collection_name[0]
            old_collection_name.objects.unlink(spine_mesh)

            new_collection_name = spine_mesh.name
            new_collection = bpy.data.collections.new(new_collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            new_collection.objects.link(spine_mesh)
        return {'FINISHED'}
    
    def find_intersecting_face_centers(self, spine_list, slicer_list):
        print("finding intersecting_face_centers")
        face_centers_list = []
        intersection_normal_vector_list = []
        found_slicer = ''
        spines_without_bases = []
    
        for spine in spine_list:            
            for slicer in slicer_list:
                #Check for intersections
                results = bmesh_check_intersect_objects(spine, slicer)
                #make a BVH tree for the slicer and find the intersection normal vector
                if results[0] == True and len(results[1]) > 0:
                    slicer_bm = bmesh.new()
                    slicer_bm.from_mesh(bpy.context.scene.objects[slicer.name].data) 
                    slicer_bm.transform(slicer.matrix_world)
                    slicer_bm.faces.ensure_lookup_table() 
                    slicer_bvh = BVHTree.FromBMesh(slicer_bm)
                    print(spine.name, "normal vector", results[1] )
                    intersection_normal_vector_list.append(results[1])
                    found_slicer = slicer.name
                    break
                   
            #Handle spines that were missed
            if len(found_slicer) == 0:
                intersection_normal_vector_list.append('missing')
                face_centers_list.append('missing')
                spines_without_bases.append(spine.name)
                for collection in spine.users_collection:
                    collection.objects.unlink(spine)
                    bpy.data.collections.remove(collection)
                    bpy.context.scene.collection.objects.link(spine)
                continue

            # Make a BVHtree, use it to find overlapping polygons between spine and slicer
            found_slicer = ''
            face_centers = []
            # Get the active object and its mesh
            spine_mesh = bmesh.new()
            spine_mesh.from_mesh(bpy.context.scene.objects[spine.name].data)
            spine_mesh.transform(spine.matrix_world)
            spine_mesh.faces.ensure_lookup_table() 

            # Create a BVHTree for the mesh
            spine_bvh = BVHTree.FromBMesh(spine_mesh)
            overlap = slicer_bvh.overlap(spine_bvh) #overlap is list containing pairs of polygon indices, the first index referencing the slicer tree, the second referencing the spine tree.
            overlapping_spine_face_index_list = [pair[1] for pair in overlap]

            for face_index in overlapping_spine_face_index_list:
                face_data =spine_mesh.faces[face_index]                
                face_centers.append(face_data.calc_center_median())
            
            face_centers_list.append([face_centers])
            face_centers = []
            spine_mesh.free()
            slicer_bm.free()
        print("spines_without_bases", spines_without_bases)
        return(face_centers_list, intersection_normal_vector_list)     

    
    def find_spine_base(self, face_centers_list):
        spine_base_list = []

        print("finding base")
        for face_centers_collection in face_centers_list:
                         
            if face_centers_collection[0] == [] or face_centers_collection == 'missing':
                spine_base_list.append('missing')
                continue

            # elif len(face_centers_collection[0]) == 1:
            #     spine_base_coords = [face_centers_collection[0]]
            #     print(spine_base_coords, "coords to unpack")
            #     spine_base_mesh = bpy.data.meshes.new("Spine Base")
            #     spine_base_mesh.from_pydata(spine_base_coords, [], [])
            #     spine_base_list.append(spine_base_mesh)
         
            else:
                face_centers_collection = face_centers_collection[0]

                #Add spine base as Mesh to Blender
                spine_base_mesh = bpy.data.meshes.new("Spine Base")  # add the new mesh

                #Find the center of the overlapping polygons and store it in "Spine Base"

                x, y, z = [ sum( [v[i] for v in face_centers_collection] ) for i in range(3)] #Tested: This does need to be 3
                count = float(len(face_centers_collection))
                spine_base = Vector( (x, y, z ) ) / count        
                spine_base_coords = [spine_base]
                spine_base_mesh.from_pydata(spine_base_coords, [], [])
                spine_base_list.append(spine_base_mesh)

        print("bases lost?", "16", spine_base_list[15], "24", spine_base_list[23])
        return(spine_base_list)
    
    def find_spine_tip(self, spine_list, spine_base_list, intersection_normal_vector_list):
        print("finding tip")
        print(len(spine_base_list), "spine_base_list")
        print(len(spine_list), "spine_list")
        print(len(intersection_normal_vector_list), "intersection_normal_vector_list")

        spine_tip_list = []
        counter = 0

        for spine in spine_list:
            #print(spine.name, "Cycle #", counter)
            spine_length_dict = {}
            spine_coordinates_dict = {}
            spine_base = spine_base_list[counter]

            if spine_base == 'missing':
                print(spine.name, "is missing its base")
                counter += 1
                spine_tip_list.append('missing')
                continue

            #Check to see if it's a stubby spine and use the Raycast method to determine Length
            elif spine.name.startswith("Stubby",0, 8):         
                depsgraph = bpy.context.evaluated_depsgraph_get()
                ray_direction = intersection_normal_vector_list[counter] 
                print(spine.name, "ray direction", ray_direction)
                ray_max_distance = 100
                ray_cast = bpy.context.scene.ray_cast(depsgraph, spine_base.vertices[0].co, ray_direction, distance = ray_max_distance)
                spine_tip = ray_cast[1]
                spine_tip_list.append(spine_tip)
                counter += 1

            elif spine_base != 'missing' and spine.name.startswith("Stubby",0, 8) == False:
                print(spine.name, "entering brute force")
                #Otherwise use brute force method
                for vert in spine.data.vertices:
                #for vert in spine.verts:
                    length = math.dist(vert.co, spine_base.vertices[0].co)         
                    spine_length_dict[vert.index] = length
                    spine_coordinates_dict[vert.index] = vert.co                

                spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
                spine_tip = spine_coordinates_dict[spine_tip_index]
                spine_tip_list.append(spine_tip)
                counter += 1
            else:
                print(spine.name, "missing base")
                spine_tip_list.append('missing')
                counter += 1

        print(len(spine_tip_list), "spine_tip_list")
        return(spine_tip_list)

    def create_base_and_tip(self, spine_list, spine_base_list, spine_tip_list):
        print("creating base and tip")
        print("tip list length", len(spine_tip_list))
        edges = []
        faces = []
        counter = 0
        
        for spine in spine_list:
            #remove mesh from collection
            spine_base = spine_base_list[counter]          
            spine_tip = spine_tip_list[counter]
            spine_name = spine_list[counter]
            if spine_base != 'missing':
                spine_base = spine_base.vertices[0].co
            else:
                counter += 1
                continue

            #Compare the distance between Spine Base and all other verticies in spine_mesh and store in "spine_length_dict"   
            spine_length_dict = {}
            spine_coordinates_dict = {}
                                    
            for vert in spine.data.vertices:
            #for vert in spine_mesh.verts:
                length = math.dist(vert.co, spine_base)         
                spine_length_dict[vert.index] = length
                spine_coordinates_dict[vert.index] = vert.co                

            spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
            spine_tip = spine_coordinates_dict[spine_tip_index]

            #Clear dictionary between loops    
            spine_length_dict = {}
            spine_coordinates_dict = {}

            #Create a mesh with spine_base and spine_tip
           
            endpoint_mesh = bpy.data.meshes.new(spine_name.name)  # add the new mesh
            endpoint_mesh_name = "endpoints_" + str(spine_name.name)
            obj = bpy.data.objects.new(endpoint_mesh_name, endpoint_mesh)

            #Put the endpoint mesh into the same folder as its spine
            collection = bpy.context.scene.collection.children.get(spine_name.name)
            if not collection:
                pass
            else:
                collection.objects.link(obj)
                                
            verts = [spine_base, spine_tip]
    
            endpoint_mesh.from_pydata(verts, edges, faces)
            counter += 1

        return {'FINISHED'}          
    

    def execute(self, context):
        print("entering execute")
        spine_and_slicers = self.get_spines()
        spine_list = spine_and_slicers[0]
        slicer_list = spine_and_slicers[1]
        self.spines_to_collections(spine_list)
        #self.find_intersections(spine_list, slicer_list)
        face_centers_and_normal_vectors = self.find_intersecting_face_centers(spine_list,slicer_list)
        face_centers_list = face_centers_and_normal_vectors[0]
        #print("face centers in execute", len(face_centers_list))
        intersection_normals = face_centers_and_normal_vectors[1] 
        spine_base_list = self.find_spine_base(face_centers_list)
        spine_tip_list = self.find_spine_tip(spine_list, spine_base_list, intersection_normals)
        self.create_base_and_tip(spine_list, spine_base_list, spine_tip_list)
        return {'FINISHED'}




#This class is used to make endpoints for spines that weren't automatically segmented
    #Get selected vertex/verticies, find their center and turn them into a vector called "Spine Base"
    #Compare Spine base with other vertices to find Spine Tip at the maximum distance from Spine Base
    #Create Spine base and Tip in the collection of the original spine mesh

class ManualLength(bpy.types.Operator):
    bl_idname = 'object.individual_length_finder' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Manual Length'

    #Get selected verticies
    def FindSelectedVerts(self):
        print("Finding selected vertices")
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        vert_list = []
        for v in bpy.context.active_object.data.vertices:
            if v.select:
                vert_list.append(v)
            else:
                pass
        
        print("Original vertex coords", vert_list[0])
        bpy.ops.object.mode_set(mode=mode)
        return(vert_list)
    
    #Given several selected verticies find the center
    def FindSpineBase(self,vert_list):
        print("Finding spine base")
        x, y, z = [ sum( [v.co[i] for v in vert_list] ) for i in range(3)] #Tested this - it does need to be 3
        count = float(len(vert_list))
        spine_base = Vector( (x, y, z ) ) / count        

        return(spine_base)

    #Compare the distance between the spine base and all other verices to find the farthest point
    def FindSpineTip(self, spine_base):
        print("Finding spine tip")
        spine_length_dict = {}
        spine_coordinates_dict = {}
                                    
        for vert in bpy.context.active_object.data.vertices:
            length = math.dist(vert.co, spine_base)         
            spine_length_dict[vert.index] = length
            spine_coordinates_dict[vert.index] = vert.co                

        spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
        spine_tip = spine_coordinates_dict[spine_tip_index]

        print("spine_tip", spine_tip)
        return(spine_tip)

    def CreateEndpointMesh(self, spine_base, spine_tip):
        #Use the spine base and spine tip coordinates to create points in active object's collection
        #Get active object
        obj = bpy.context.object
        
        #Make a mesh
        edges = []
        faces = []
        verts = [spine_base, spine_tip]    
        endpoint_mesh = bpy.data.meshes.new("endpoints_" + str(obj.name))  
        endpoint_mesh.from_pydata(verts, edges, faces)

        #Use the selected object's coordinates for reference frame
        endpoint_mesh.transform(obj.matrix_world)

        #Link to active object's collection
        collection = obj.users_collection[0]        
            
        endpoints = bpy.data.objects.new(endpoint_mesh.name, endpoint_mesh)
        
        collection.objects.link(endpoints)
        return {'FINISHED'}
    
    def execute(self, context):
        print("Executing")
        vert_list = self.FindSelectedVerts()
        spine_base = self.FindSpineBase(vert_list)
        spine_tip = self.FindSpineTip(spine_base)
        self.CreateEndpointMesh(spine_base, spine_tip)
        return {'FINISHED'}

#This class was created to deal with spines composed of multiple meshes, by turning them yellow, so that they can be manually joined
#Get selected spines and store them in spine_list
#Make BVH trees of the spines and store them spine_BVHtree_list
#Iterate over spine_BVHtree_list to find the indices of overlapping spines
#Use spine indices to color the overlapping spines in spine list

class ManualMerge(bpy.types.Operator):
    bl_idname = 'object.manual_merge' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Show fractured spines'

    #Get selected spines and store them in spine_list
    def get_spines(self):
        #Get selected spines
        selected_objects = bpy.context.selected_objects
        spine_list = []
        
        for spine in selected_objects:            
            spine_list.append(spine)    
        #return(spine_list, spine_BVHtree_list)
        return(spine_list)    
    
    #Make BVH trees of the spines and store them spine_BVHtree_list
    def spine_bvh_trees(self, spine_list):
        spine_BVHtree_list = []

        for spine in spine_list:            
            spine_mesh = bmesh.new()
            spine_mesh.from_mesh(bpy.context.scene.objects[spine.name].data)
            spine_mesh.transform(spine.matrix_world)
            spine_BVHtree = BVHTree.FromBMesh(spine_mesh)
            spine_BVHtree_list.append(spine_BVHtree)

        return(spine_BVHtree_list)
        
    #Iterate over spine_BVHtree_list to find the indices of overlapping spines
    def find_overlapping_spines(self, spine_BVHtree_list):
        overlapping_spine_index_list = []
        print("spine_BVHtree_list in find overlapping", spine_BVHtree_list)
        counter = 0

        for bvh_tree in spine_BVHtree_list:            
            current_spine_tree = spine_BVHtree_list[counter]
            if counter == spine_BVHtree_list.index(bvh_tree): #Spines will always overlap themselves...
                continue
            elif current_spine_tree.overlap(bvh_tree):
                overlapping_spine_index_list.append(spine_BVHtree_list.index(bvh_tree))
            counter += 1
        print("overlapping_spine_index_list", overlapping_spine_index_list)
        return(overlapping_spine_index_list)

    #Use spine indices to color the overlapping spines in spine list
    def color_overlapping_spines(self, overlapping_spine_index_list, spine_list):
        spines_to_color = []

        for i in overlapping_spine_index_list:
            spines_to_color.append(spine_list[i])

        for spine in spines_to_color:
            spine.data.materials.clear()
            spine.select_set(True)
            spine.color = (1,1,0,1)        
            mat = bpy.data.materials.new("Blue")

            # Activate its nodes
            mat.use_nodes = True

            # Get the principled BSDF (created by default)
            principled = mat.node_tree.nodes['Principled BSDF']

            # Assign the color
            principled.inputs['Base Color'].default_value = (1,1,0,1)
            # Assign the material to the object
            spine.data.materials.append(mat)
        return {'FINISHED'}

    def execute(self, context):
        spine_list = self.get_spines()
        spine_BVHtree_list = self.spine_bvh_trees(spine_list)
        overlapping_spine_index_list = self.find_overlapping_spines(spine_BVHtree_list)
        self.color_overlapping_spines(overlapping_spine_index_list, spine_list)
    
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

#This class contains methods which extract data from the text-entry panel, meshes, and endpoints and the writes them to an NWB File
class WriteNWB(bpy.types.Operator):
    bl_idname = 'object.write_nwb' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Write NWB File'

    #Extract strings and floats from text entry panel
    def AddPanelData(self):
        subject_id = bpy.context.scene.subject_id 
        age = bpy.context.scene.age
        #subject_description = bpy.context.scene.subject_description
        genotype = bpy.context.scene.genotype
        sex = bpy.context.scene.sex
        species = bpy.context.scene.species
        strain = bpy.context.scene.strain
        #Extract NWBfile Strings
        experimenter = bpy.context.scene.experimenter
        experiment_description = bpy.context.scene.experiment_description
        identifier = bpy.context.scene.identifier
        institution = bpy.context.scene.institution
        lab = bpy.context.scene.lab
        notes = bpy.context.scene.notes
        pharmacology = bpy.context.scene.pharmacology
        protocol =  bpy.context.scene.protocol
        session_start_time = bpy.context.scene.session_start_time
        session_start_time = datetime.strptime(session_start_time, '%Y-%m-%d %H:%M:%S')      
        session_description = bpy.context.scene.session_description
        slices = bpy.context.scene.slices
        surgery = bpy.context.scene.surgery

        #Extract Imaging Plane Strings
        plane_name = bpy.context.scene.plane_name
        plane_description = bpy.context.scene.plane_description
        excitation_lambda = float(bpy.context.scene.excitation_lambda)
        external_file = [bpy.context.scene.external_file]
        grid_spacing = bpy.context.scene.grid_spacing
        imaging_rate = float(bpy.context.scene.imaging_rate)
        indicator = bpy.context.scene.indicator
        location = bpy.context.scene.location
        grid_spacing_unit = bpy.context.scene.grid_spacing_unit
        
        #Create filename 
        nwbfile_name = subject_id + identifier + '.nwb'

        #Create pynwb subject
        subject = Subject(
            age = age,
            #description = subject_description,
            genotype = genotype,
            sex = sex,
            species = species,
            strain = strain,
            subject_id = subject_id
            )

        #Create pywnb File
        nwbfile = NWBFile(
            experimenter = experimenter,
            experiment_description = experiment_description,
            file_create_date = datetime.now(),
            identifier = identifier,
            institution = institution,
            lab = lab,
            notes = notes, 
            pharmacology = pharmacology,
            protocol = protocol,
            session_description = session_description,
            session_start_time = session_start_time,
            slices = slices,
            surgery = surgery, 
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
            grid_spacing = [grid_spacing, grid_spacing, grid_spacing], 
            grid_spacing_unit = grid_spacing_unit)

        #Create image series and add a link to the raw image stack to the file
        raw_data = image.ImageSeries(
            'Raw Data',
            format = 'external',
            rate = imaging_rate, #Unit is Hz
            external_file = external_file, 
            starting_frame = [1])

        nwbfile.add_acquisition(raw_data)
        return(nwbfile, imaging_plane, raw_data, nwbfile_name)
    
    #Find the distance between the endpoints of spines when running the execute loop
    def find_length(self, i):
        point1 = i.data.vertices[0].co
        point2 = i.data.vertices[1].co
        length = math.dist(point1, point2)
        print("spine name is", i.name, "length is ", length)
        #return length
        return point1, point2


    #This purports to be a faster way             
    def distance_vec(self, i, point1: Vector, point2: Vector) -> float:
        point1 = i.data.vertices[0].co
        point2 = i.data.vertices[1].co
        #Calculate distance between two points.
        length = (point2 - point1).length
        print("spine name is", i.name, "vector length is ", length)
        return length

    #Extract attributes from spine meshes when running the execute loop
    def find_mesh_attributes(self, i):                  
        #Create and find center of mass
        i.select_set(True) #The origin_set operator only works on selected object
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
        center_of_mass = i.location
        center_of_mass = [center_of_mass[0], center_of_mass[1], center_of_mass[2]]
    
        #Get mesh data from the active object in the Scene Collection
        mesh = i.data
        #Create an empty BMesh
        bm = bmesh.new()
        #Fill Bmesh with the mesh data from the object  
        bm.from_mesh(mesh)

        #Find Volume
        volume = bm.calc_volume(signed=False)

        #Find Surface Area
        surface_area = sum(i.calc_area() for i in bm.faces)
        
        bm.free()
        return center_of_mass, volume, surface_area
    
    #Extract data and pass to file
    def execute(self, context):
        #Extract Panel Data
        holder = self.AddPanelData()
        nwbfile = holder[0]
        imaging_plane = holder[1]
        raw_data = holder[2]
        nwbfile_name = holder[3]
        
        #Empty variables which are collected during the loop
        # length = ''
        # center_of_mass = ''
        # volume = ''
        # surface_area = ''

        module = nwbfile.create_processing_module("SpineData", 'Contains processed neuromorphology data from Blender.')
        image_segmentation = ImageSegmentation()
        module.add(image_segmentation)

        #This loop iterates through all collections and extracts data about the meshes.
       
        for collection in bpy.data.collections:
            #Create processing module
            #module = nwbfile.create_processing_module(collection.name, 'contains processed neuromorphology data from Blender')
            #Create image segmentation
            #image_segmentation = ImageSegmentation()
            #Add the image segmentation to the module

            #Empty variables which are collected during the loop
            length = ''
            center_of_mass = ''
            volume = ''
            surface_area = ''

            #Create unique name
            segmentation_name = collection.name + ' mesh plane_segmentaton'
            print("segmentation_name", segmentation_name)

            #Create plane segmentation from our NWB extension    
            plane_segmentation = image_segmentation.create_plane_segmentation(
                name = segmentation_name,
                description = 'output from segmenting a mesh in Blender',
                imaging_plane = imaging_plane,     
                reference_images = raw_data
                    )               

            #Iterate through collections and extract variables
            for i in collection.objects:

                if i.type == 'MESH' and len(i.data.vertices) == 2:
                    length_holder = self.find_length(i)
                    point1 = length_holder[0]
                    point2 = length_holder[1]
                    length = self.distance_vec(i, point1, point2)

                elif i.type == 'MESH' and len(i.data.vertices) > 2:
                    mesh_attributes = self.find_mesh_attributes(i)
                    center_of_mass = mesh_attributes[0]
                    volume = mesh_attributes[1]
                    surface_area = mesh_attributes[2]

            #Add columns to ROI to hold extracted variables
            plane_segmentation.add_column('center_of_mass', 'center_of_mass')
            plane_segmentation.add_column('volume', 'volume')
            plane_segmentation.add_column('surface_area', 'surface_area')         
            plane_segmentation.add_column('length', 'length')

            plane_segmentation.add_roi(
                image_mask=np.ones((4,4)), #This line holds dummy data and won't work without it.
                # faces=faces,
                # vertices=vertices,
                center_of_mass = center_of_mass,
                volume=volume,
                surface_area = surface_area,
                length = length,
                )
                   
                #This code can be used to extract the verticies and faces if we want to keep them in the NWBFile
                #NOTE: edges should be included if we decide to do that

                #     # for v in bm.verts:
                #     #     mesh_verts.append(v.co)
                
                #     # for face in mesh.polygons:
                #     #     vertices = face.vertices
                #     #     face_vert_list = [vertices[0], vertices[1], vertices[2]]
                #     #     faces.append(face_vert_list)

        os.chdir('C:/Users/meowm/Downloads') #TODO: How do I handle this for the final version?
        #Write the NWB file
        with NWBHDF5IO(nwbfile_name, 'w') as io:
            io.write(nwbfile)

        return {'FINISHED'}

def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """
    Returns a transformed, triangulated copy of the mesh
    """

    assert(obj.type == 'MESH')

    if apply_modifiers and obj.modifiers:
        me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=False)
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    # Remove custom data layers to save memory
    for elem in (bm.faces, bm.edges, bm.verts, bm.loops):
        for layers_name in dir(elem.layers):
            if not layers_name.startswith("_"):
                layers = getattr(elem.layers, layers_name)
                for layer_name, layer in layers.items():
                    layers.remove(layer)

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm

def bmesh_check_intersect_objects(obj, obj2):
    """
    Check if any faces intersect with the other object

    returns a boolean
    """
    assert(obj != obj2)

    # Triangulate
    bm = bmesh_copy_from_object(obj, transform=True, triangulate=True)
    bm2 = bmesh_copy_from_object(obj2, transform=True, triangulate=True)

    # If bm has more edges, use bm2 instead for looping over its edges
    # (so we cast less rays from the simpler object to the more complex object)
    if len(bm.edges) > len(bm2.edges):
        bm2, bm = bm, bm2

    # Create a real mesh (lame!)
    scene = bpy.context.scene
    me_tmp = bpy.data.meshes.new(name="~temp~")
    bm2.to_mesh(me_tmp)
    bm2.free()
    obj_tmp = bpy.data.objects.new(name=me_tmp.name, object_data=me_tmp)
    # scene.objects.link(obj_tmp)
    bpy.context.collection.objects.link(obj_tmp)
    ray_cast = obj_tmp.ray_cast

    intersect = False

    EPS_NORMAL = 0.000001
    EPS_CENTER = 0.01  # should always be bigger

    hit_normal = []
    #for ed in me_tmp.edges:
    for ed in bm.edges:
        v1, v2 = ed.verts

        # setup the edge with an offset
        co_1 = v1.co.copy()
        co_2 = v2.co.copy()
        co_mid = (co_1 + co_2) * 0.5
        no_mid = (v1.normal + v2.normal).normalized() * EPS_NORMAL
        co_1 = co_1.lerp(co_mid, EPS_CENTER) + no_mid
        co_2 = co_2.lerp(co_mid, EPS_CENTER) + no_mid

        success, co, no, index = ray_cast(co_1, (co_2 - co_1).normalized(), distance = ed.calc_length())
        
        if index != -1:
            intersect = True
            #cast = ray_cast(co_1, (co_2 - co_1).normalized(), distance = ed.calc_length())
            cast = ray_cast(co_1, (co_2 - co_1).normalized(), distance = 100)
            hit_normal = cast[2]
            #print(hit_normal)
            break

    

    # scene.objects.unlink(obj_tmp)
    bpy.context.collection.objects.unlink(obj_tmp)
    bpy.data.objects.remove(obj_tmp)
    bpy.data.meshes.remove(me_tmp)


    return intersect, hit_normal
# obj = bpy.context.object
# obj2 = (ob for ob in bpy.context.selected_objects if ob != obj).__next__()
# intersect = bmesh_check_intersect_objects(obj, obj2)

# print("There are%s intersections." % ("" if intersect else " NO"))

