import bpy
import bmesh
import mathutils
import os
import numpy as np 
from datetime import datetime
import math
from collections import defaultdict
import time


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

        #Add button that generates spheres for Check Boolean error handling        
        row = layout.row()
        row.operator('object.add_spheres', text = 'Add Sphere Markers')

        #Add button that evaluates Booleans        
        row = layout.row()
        row.operator('object.check_booleans', text = 'Check Slicers')

        #Add button that evaluates Booleans        
        row = layout.row()
        row.operator('object.slice_spines', text = 'Slice Spines')
        
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

#Slice off Spines
class SpineSlicer(bpy.types.Operator):
    bl_idname = 'object.slice_spines' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Slice Spines' 

    def execute(self, context):
        start_time = time.time()
        #Select active object
        object = bpy.context.active_object
        #Split it into pieces
        bpy.ops.mesh.separate(type='LOOSE')
        spine_list = [obj for obj in bpy.context.selected_objects]
        #Find the largest mesh and remove it from the list
        max_verts = 0
        dendrite = ""
        for o in spine_list:
            if len(o.data.vertices) > max_verts:
                max_verts = len(o.data.vertices)
                dendrite = o.name
        dendrite = bpy.data.objects[dendrite]
        spine_list.remove(dendrite)

        # Get the active collection, its name, and put its contents into slicer list
        collection = bpy.context.collection
        collection_name = collection.name
        boolean_meshes_collection = bpy.data.collections[collection_name]
        slicer_list = [obj for obj in boolean_meshes_collection.objects]

        faces_and_spine_slicer_pairs = find_overlapping_spine_faces(self, spine_list, slicer_list)
        spine_overlapping_indices_dict = faces_and_spine_slicer_pairs[0]
        spine_and_slicer_dict = faces_and_spine_slicer_pairs[1]
        spines_to_collections(self, spine_and_slicer_dict)
        #paint_spines(self, spine_and_slicer_dict)
        spine_base_dict = find_spine_bases(self, spine_overlapping_indices_dict, spine_and_slicer_dict)
        spine_tip_dict = find_spine_tip(self, spine_base_dict)
        create_base_and_tip(self, spine_base_dict, spine_tip_dict)
        create_surface_area_mesh(self, spine_and_slicer_dict)


        return {'FINISHED'}

def create_surface_area_mesh(self, spine_and_slicer_dict):
    surface_spine_and_slicer_dict = {}
    # Iterate over the spine and slicer dictionary
    for spine, slicer in spine_and_slicer_dict.items():
        spine = bpy.data.objects[spine]
        slicer = bpy.data.objects[slicer]

        # Create a copy of the spine, add surface area to its name
        duplicate_spine = spine.copy()
        duplicate_spine.data = spine.data.copy()
        duplicate_spine.name = "surface_" + spine.name

        # Link the duplicate spine to the same collection as the original spine
        spine_collection = spine.users_collection[0]
        spine_collection.objects.link(duplicate_spine)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select the duplicate spine and make it the active object
        duplicate_spine.select_set(True)
        bpy.context.view_layer.objects.active = duplicate_spine

        # Create the Solidify modifier
        solidify_modifier = duplicate_spine.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify_modifier.thickness = 0.01  # Adjust the thickness value as desired

        # Apply the Solidify modifier
        bpy.ops.object.modifier_apply({"object": duplicate_spine}, modifier=solidify_modifier.name)

        # Deselect the duplicate spine
        duplicate_spine.select_set(False)

        # Store the relationship between the duplicate spine and slicer in the dictionary
        surface_spine_and_slicer_dict[duplicate_spine.name] = slicer

    print(surface_spine_and_slicer_dict) 
    return(surface_spine_and_slicer_dict)
    # for spine, slicer in spine_and_slicer_dict.items():
    #     print(spine, 'spine', slicer, 'slicer')
    #     spine = bpy.data.objects[spine]
    #     slicer = bpy.data.objects[slicer]
    #     #get its slicer, set z to be 0.01
    #     overlap = 0.01
        
    #     slicer.dimensions.z = overlap
    #     #Create a copy of the spine, add surface area to its name
    #     duplicate_spine = spine.copy()
    #     duplicate_spine.data = spine.data.copy()
    #     duplicate_spine.name = "surface_" + spine.name

    #     # Link the duplicate spine to the same collection as the original spine
    #     spine_collection = spine.users_collection[0]
    #     spine_collection.objects.link(duplicate_spine)

    #     # Deselect all objects
    #     bpy.ops.object.select_all(action='DESELECT')

    #     # Select the duplicate spine and make it the active object
    #     duplicate_spine.select_set(True)
    #     bpy.context.view_layer.objects.active = duplicate_spine

    #     # Create the Solidify modifier
    #     solidify_modifier = duplicate_spine.modifiers.new(name="Solidify", type='SOLIDIFY')
    #     solidify_modifier.thickness = 0.1  # Adjust the thickness value as desired

    #     # Apply the Solidify modifier
    #     bpy.ops.object.modifier_apply({"object": duplicate_spine}, modifier=solidify_modifier.name)

    #     duplicate_spine.select_set(False)

        #Apply solidify modifier to it
        #Apply slicer boolean modifier

 
#For our use original_mesh_name means dendrite, booleans refers to cylinders/slicers  
class CheckBooleans(bpy.types.Operator):
    bl_idname = 'object.check_booleans' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Check Booleans'   

    def execute(self, context):
        start_time = time.time()
        
        vert_threshold = 1000

        #Get objects to perform Boolean on/with
        boolean_objects = get_objects_for_boolean(self, context)
        original_mesh = boolean_objects[0]
        boolean_meshes_collection = boolean_objects[1]
        original_mesh_copy = boolean_objects[2]
        #original_mesh_verts = boolean_objects[3]
        sphere1 = boolean_objects[3]
        sphere2 = boolean_objects[4]
        object_collection = boolean_objects[5]

        try_booleans(self, boolean_meshes_collection, vert_threshold, original_mesh, original_mesh_copy,  sphere1, sphere2, object_collection)
        bpy.data.objects.remove(original_mesh, do_unlink=True)
        bpy.data.objects.remove(original_mesh_copy, do_unlink=True)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Elapsed time:", elapsed_time, "seconds")

        return {'FINISHED'}

def get_objects_for_boolean(self, context):
    # Get the active object and its name
    object = bpy.context.active_object
    object_collection = object.users_collection[0]

    # Get the active collection and its name
    collection = bpy.context.collection
    collection_name = collection.name

    # Get references to the original mesh and the collection
    original_mesh = bpy.data.objects[object.name]
    original_mesh = bpy.context.view_layer.objects.active
    boolean_meshes_collection = bpy.data.collections[collection_name]
    original_mesh.select_set(True)

    # Store the original mesh data
    original_mesh_copy = original_mesh.copy()
    original_mesh_copy.data = original_mesh.data.copy()
    # original_mesh_verts = len(original_mesh.data.vertices)

    sphere1 = bpy.context.scene.objects.get("BoolSphere1")
    sphere2 = bpy.context.scene.objects.get("BoolSphere2")

    if not sphere1:
        print("Please add Spheres")

    return(original_mesh, boolean_meshes_collection, original_mesh_copy, sphere1,sphere2, object_collection)

def try_booleans(self, boolean_meshes_collection, vert_threshold, original_mesh, original_mesh_copy, sphere1, sphere2, object_collection):
    for obj in boolean_meshes_collection.objects:
        # Create the boolean modifier 
        bool_modifier = original_mesh.modifiers.new(name="Boolean", type='BOOLEAN')
        bool_modifier.operation = 'DIFFERENCE'
        bool_modifier.object = obj

        # Apply the modifier to the active object
        bpy.ops.object.modifier_apply(modifier=bool_modifier.name)

        # Run the raycast between the two spheres
        hit = CheckBoolsRayCast(sphere1, sphere2)
        print("hit?", hit)
        
        if hit:
            print(obj.name, len(original_mesh.data.vertices), "has issues", 'copy:', len(original_mesh_copy.data.vertices))

            # Create a new original_mesh object from the original_mesh_copy
            original_mesh = original_mesh_copy.copy()
            original_mesh.data = original_mesh_copy.data.copy()

            # Unlink the previous original_mesh from the scene collection
            #bpy.context.collection.objects.unlink(original_mesh)
            #bpy.data.collections[object_collection.name].objects.link(obj)
            # Link the new original_mesh to the scene collection
            # Get the scene collection
            scene_collection = bpy.context.scene.collection

            # Link the object to the scene collection
            scene_collection.objects.link(original_mesh)
            #bpy.context.collection.objects.link(original_mesh)
            # original_mesh.select_set(True)

            # # Update the boolean modifier object reference
            # bool_modifier.object = obj

            obj.name = obj.name + " needs inspection"

        if not hit:
            #Absence of hit means object is between spheres
            print("Dendrite detected. Good to go!")
            print(obj.name, len(original_mesh.data.vertices), "success")
            original_mesh_verts = len(original_mesh.data.vertices)


    return {'FINISHED'}

# Add spheres for Check Booleans
class AddSpheres(bpy.types.Operator):
    bl_idname = 'object.add_spheres'
    bl_label = 'Add Spheres'

    def execute(self, context):
        # Create two icospheres
        bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 0))
        sphere1 = bpy.context.object
        bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 3))
        sphere2 = bpy.context.object

        # Rename the icospheres
        sphere1.name = "BoolSphere1"
        sphere2.name = "BoolSphere2"

        return {'FINISHED'}

# def try_booleans(self, boolean_meshes_collection, vert_threshold, original_mesh, original_mesh_copy, original_mesh_verts, sphere1, sphere2):
#     for obj in boolean_meshes_collection.objects:
        
#         # Create the boolean modifier 
#         bool_modifier = original_mesh.modifiers.new(name="Boolean", type='BOOLEAN')
#         bool_modifier.operation = 'DIFFERENCE'
#         bool_modifier.object = obj
#         original_mesh.select_set(True)

#         # Apply the modifier to the active object
#         bpy.ops.object.modifier_apply(modifier=bool_modifier.name)
        
#         # Run the raycast between the two spheres
#         hit = CheckBoolsRayCast(sphere1, sphere2)
        
#         if hit:
#             print("Dendrite detected. Good to go!")
#             print(obj.name, len(original_mesh.data.vertices), "success")
#             original_mesh_verts = len(original_mesh.data.vertices)

#         if not hit:
#             print(obj.name, len(original_mesh.data.vertices), "has issues", 'copy:', len(original_mesh_copy.data.vertices))

#             # Unlink the previous original_mesh from the scene collection
#             bpy.context.scene.collection.objects.unlink(original_mesh)

#             # Create a new original_mesh object from the original_mesh_copy
#             original_mesh = original_mesh_copy.copy()
#             original_mesh.data = original_mesh_copy.data.copy()

#             # Link the new original_mesh to the scene collection
#             bpy.context.collection.objects.link(original_mesh)
#             original_mesh.select_set(True)

#             # Update the boolean modifier object reference
#             bool_modifier.object = obj

#             obj.name = obj.name + " needs inspection"
#     return {'FINISHED'}

# def try_booleans(self, boolean_meshes_collection, vert_threshold, original_mesh, original_mesh_copy, original_mesh_verts,sphere1,sphere2):
#     for obj in boolean_meshes_collection.objects:
#         print("modifying object", original_mesh.name)
        
#         # Create the boolean modifier 
#         bool_modifier = original_mesh.modifiers.new(name="Boolean", type='BOOLEAN')
#         bool_modifier.operation = 'DIFFERENCE'
#         bool_modifier.object = obj

#         # Check if original_mesh is in the scene collection before unlinking
#         if original_mesh.name in bpy.context.scene.collection.objects:
#             bpy.context.scene.collection.objects.unlink(original_mesh)

#         # Link the modified original_mesh to the scene collection
#         bpy.context.scene.collection.objects.link(original_mesh)
#         original_mesh.select_set(True)

#         # Set the active object to original_mesh
#         bpy.context.view_layer.objects.active = original_mesh

#         # Apply the modifier to the active object
#         bpy.ops.object.modifier_apply(modifier=bool_modifier.name)
        
#         #Run a raycast between two spheres a fixed distance apart, on either side of the dendrite
#         hit, location, normal, face_index = CheckBoolsRayCast(self, sphere1, sphere2)
#         if hit:
#             print("Dendrite detected, gtg")

#         #If it hits the target spere, fail.  (The dendrite should be blocking)

#         # Check to see how well the Boolean worked and apply error handling
#         # Use the difference in vertices to determine if the original mesh was deleted

#         if original_mesh_verts - len(original_mesh.data.vertices) > vert_threshold:
#             print(obj.name, len(original_mesh.data.vertices), "has issues", 'copy:', len(original_mesh_copy.data.vertices))

#             # Unlink the previous original_mesh from the scene collection
#             bpy.context.scene.collection.objects.unlink(original_mesh)

#             # Create a new original_mesh object from the original_mesh_copy
#             original_mesh = original_mesh_copy.copy()
#             original_mesh.data = original_mesh_copy.data.copy()

#             # Link the new original_mesh to the scene collection
#             bpy.context.scene.collection.objects.link(original_mesh)
#             original_mesh.select_set(True)

#             # Update the boolean modifier object reference
#             bool_modifier.object = obj

#             obj.name = obj.name + " needs inspection"

#         else:
#             print(obj.name, len(original_mesh.data.vertices), "success")
#             original_mesh_verts = len(original_mesh.data.vertices)
#     return {'FINISHED'}

def CheckBoolsRayCast(sphere1, sphere2):    
    # Define the start and end points for the raycast
    start_point = sphere1.location
    end_point = sphere2.location

    # Perform the raycast
    direction = end_point - start_point
    direction.normalize()

    # Check for intersections with objects
    found_intersection = False
    for obj in bpy.context.scene.objects:
        if obj != sphere1 and obj != sphere2:
            hit, location, normal, face_index = obj.ray_cast(start_point, direction)
            if hit:
                found_intersection = True
                break

    # Check if an object was found between the spheres
    if found_intersection:
        print("There is an object between the spheres.")
    else:
        print("There is no object between the spheres.")
    
    return hit

# def CheckBoolsRayCast(self, sphere1, sphere2):    
#     # Define the start and end points for the raycast
#     start_point = sphere1.location
#     end_point = sphere2.location

#     # Perform the raycast
#     direction = end_point - start_point
#     ray_length = direction.length
#     direction.normalize()

#     # Check for intersections with objects
#     found_intersection = False
#     for obj in bpy.context.scene.objects:
#         if obj != sphere1 and obj != sphere2:
#             hit, location, normal, face_index = obj.ray_cast(start_point, direction)
#             if hit:
#                 found_intersection = True
#                 break

#     # Check if an object was found between the spheres
#     if found_intersection:
#         print("There is an object between the spheres.")
#     else:
#         print("There is no object between the spheres.")
    
#     return(hit)

# ////

#Discsegmenter
#Finds spines and slicers based on selected objects
#Spines are named after their slicers and intersecting faces are found - not as reliably as it should
#Spine base is defined as the center_point of all the face intersecting points
#Spines are moved to folders, if they are missing their base, they are removed from folders
#Normals for the slicer polygons are found at the closest point to the spine center of mass
#Tips for stubby spines use the slicer normal to raycast from the spine base.  Tips for all other spines are created for the farthest vertex

class DiscSegmenter(bpy.types.Operator): 
    bl_idname = 'object.discsegmenter' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'AutoSegmenter'        
  
    def execute(self, context):
        spine_and_slicers = get_spines(self)
        spine_list = spine_and_slicers[0]
        slicer_list = spine_and_slicers[1]
        faces_and_spine_slicer_pairs = find_overlapping_spine_faces(self, spine_list, slicer_list)
        spine_overlapping_indices_dict = faces_and_spine_slicer_pairs[0]
        spine_and_slicer_dict = faces_and_spine_slicer_pairs[1]
        spines_to_collections(self, spine_and_slicer_dict)
        #paint_spines(self, spine_and_slicer_dict)
        spine_base_dict = find_spine_bases(self, spine_overlapping_indices_dict, spine_and_slicer_dict)
        spine_tip_dict = find_spine_tip(self, spine_base_dict)
        create_base_and_tip(self, spine_base_dict, spine_tip_dict)
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
        module = nwbfile.create_processing_module("SpineData", 'Contains processed neuromorphology data from Blender.')
        image_segmentation = ImageSegmentation()
        module.add(image_segmentation)

        #This loop iterates through all collections and extracts data about the meshes.
       
        for collection in bpy.data.collections:
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

#DiscSegmentor
#Put the selected meshes into spine list.  Put unselected objects into slicer list  
def get_spines(self):  
    spine_list = [mesh for mesh in bpy.context.selected_objects]

    # Get the active collection and its name
    all_obs = bpy.context.collection
    
    slicer_list = []

    for obj in all_obs.all_objects:
        slicer_list.append(obj)

    return(spine_list, slicer_list)

#Put spines into folders with their name
def spines_to_collections(self, spine_and_slicer_dict):
    #Add spines to their own folders
    for spine in spine_and_slicer_dict.keys():
        spine = bpy.data.objects.get(spine)
        old_collection_name = spine.users_collection
        old_collection_name = old_collection_name[0]
        old_collection_name.objects.unlink(spine)
        new_collection_name = spine.name
        new_collection = bpy.data.collections.new(new_collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        new_collection.objects.link(spine)
    return {'FINISHED'}

def find_overlapping_spine_faces(self, spine_list, slicer_list):
    spine_overlapping_indices_dict = {}
    spine_and_slicer_dict = {}
    spines_without_bases = []

    for spine in spine_list:
        intersects = False
        spine_bm = bmesh.new()
        spine_bm.from_mesh(bpy.context.scene.objects[spine.name].data) 
        spine_bm.transform(spine.matrix_world)
        spine_bm.faces.ensure_lookup_table() 
        spine_bvh = BVHTree.FromBMesh(spine_bm)     
        for slicer in slicer_list:
            slicer_bm = bmesh.new()
            slicer_bm.from_mesh(bpy.context.scene.objects[slicer.name].data) 
            slicer_bm.transform(slicer.matrix_world)
            slicer_bm.faces.ensure_lookup_table() 
            slicer_bvh = BVHTree.FromBMesh(slicer_bm)
            #overlap is list containing pairs of polygon indices, the first index is a vertex from the slicer mesh tree the second is from the spine mesh tree
            overlap = slicer_bvh.overlap(spine_bvh)

            if len(overlap) >= 1:
                intersects = True
                spine.name = slicer.name[6:]
                spine_overlapping_indices_dict[spine.name] = overlap
                spine_and_slicer_dict[spine.name] = slicer.name
                for collection in spine.users_collection:
                    collection.objects.unlink(spine)
                    bpy.data.collections.remove(collection)
                    bpy.context.scene.collection.objects.link(spine)
                break 

        if intersects == False:
            spines_without_bases.append(spine.name)
            for collection in spine.users_collection:
                collection.objects.unlink(spine)
                bpy.data.collections.remove(collection)
                bpy.context.scene.collection.objects.link(spine)
    
    
    print("spines without bases", spines_without_bases)
    spine_bm.free()
    slicer_bm.free()
    return(spine_overlapping_indices_dict, spine_and_slicer_dict)

#Check each spine to find its intersecting slicer.  
#Find the spine faces that intersect with the slicer and the normal vector of the slicer which is currently borked     
def find_spine_bases(self, spine_overlapping_indices_dict, modified_spine_and_slicer_dict):
    spine_base_dict = {}
    for spine in spine_overlapping_indices_dict.keys():
        face_centers = []
        face_data = []

        spine_bm = bmesh.new()
        spine = bpy.data.objects[spine]
        spine_bm.from_mesh(spine.data) 
        spine_bm.faces.ensure_lookup_table() 
        spine_bm.verts.ensure_lookup_table()

        overlap = spine_overlapping_indices_dict[spine.name]
        slicer_name = modified_spine_and_slicer_dict[spine.name]
        slicer = bpy.context.scene.objects[slicer_name]
        slicer_bm = bmesh.new()
        slicer_bm.from_mesh(slicer.data) 
        slicer_bm.faces.ensure_lookup_table() 
        slicer_bm.verts.ensure_lookup_table()
        for x,y in overlap:
            face_index = y
            face_data = spine_bm.faces[face_index]          
            face_centers.append(face_data.calc_center_median())

        face_center_mesh = bpy.data.meshes.new("face centers")  # add the new mesh
        face_center_mesh.from_pydata(face_centers, [], [])
        #Find the center of the overlapping polygons and store it in "Spine Base"
        x, y, z = [ sum( [v.co[i] for v in face_center_mesh.vertices] ) for i in range(3)] #Tested: This does need to be 3            

        count = float(len(face_centers))
        spine_base = Vector( (x, y, z ) ) / count
        
        spine_base =  spine.matrix_world @ spine_base    
        spine_base_dict[spine.name] = spine_base 

        face_centers = []
        face_data = [] 
        spine_bm.free()
        slicer_bm.free()
    return(spine_base_dict)

def find_spine_tip(self, spine_base_dict):
        spine_tip_dict = {}
        for spine in spine_base_dict.keys():
            spine_length_dict = {}
            spine_coordinates_dict = {}
            spine_base = spine_base_dict[spine]
            spine = bpy.data.objects[spine]

            #Check to see if it's a stubby spine and use a Raycast method to determine Length
            if spine.name.startswith("Stubby",0, 8): 
                tip_locations = {}
                results = cone_raycast(self, spine_base, spine)
                for location in results:
                    distance = spine.location - location
                    index =  results.index(location)
                    tip_locations[index] = distance
                farthest_location_index = get_key_with_largest_value(tip_locations)
                spine_tip_location = results[farthest_location_index]

                spine_tip = spine.matrix_world @ spine_tip_location
                 
                spine_tip_dict[spine] = spine_tip
                
                #Mark the spot
                empty = bpy.data.objects.new(name=spine.name + "tip", object_data=None)
                empty_spot = spine_tip  
                #empty_spot =  spine.matrix_world @ empty_spot        
                empty.location = empty_spot 
                # Link the empty object to the scene
                scene = bpy.context.scene
                scene.collection.objects.link(empty)        
                # Select the empty object
                empty.select_set(True)
                scene.view_layers.update()
                
            else:
                # #Compare the distance between Spine Base and all other verticies in spine_mesh and store in "spine_length_dict"   
                # spine_length_dict = {}
                # spine_coordinates_dict = {}
                                        
                # for vert in spine.data.vertices:
                #     length = math.dist(vert.co, spine_base)         
                #     spine_length_dict[vert.index] = length
                #     spine_coordinates_dict[vert.index] = vert.co                

                # spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
                # spine_tip = spine_coordinates_dict[spine_tip_index]
                # spine_tip_location = spine.matrix_world @ spine_tip

                # #Clear dictionary between loops    
                # spine_length_dict = {}
                # spine_coordinates_dict = {}
                vertices = [spine.matrix_world @ v.co for v in spine.data.vertices]            

                # Initialize the farthest distance to zero
                farthest_distance = 0.0

                # Loop through all vertices and compare distances
                for index, vertex in enumerate(vertices):
                    dist = (spine_base - vertex).length
                    if dist > farthest_distance:
                        farthest_distance = dist
                        spine_tip = vertex
                spine_tip_dict[spine] = spine_tip
                # #Mark the spot
                empty = bpy.data.objects.new(name=spine.name + "tip", object_data=None)
                empty_spot = spine_tip 
                #empty_spot =  spine.matrix_world @ empty_spot        
                empty.location = empty_spot 
                # Link the empty object to the scene
                scene = bpy.context.scene
                scene.collection.objects.link(empty)        
                # Select the empty object
                empty.select_set(True)
                scene.view_layers.update()

        return(spine_tip_dict)

#Create a mesh with spine_base and spine_tip
def create_base_and_tip(self, spine_base_dict, spine_tip_dict): 
    bpy.ops.object.select_all(action='DESELECT')  
    for spine in spine_tip_dict.keys():
        spine_base = spine_base_dict[spine.name]
        spine_tip = spine_tip_dict[spine]        
        endpoint_mesh = bpy.data.meshes.new(spine.name)  # add the new mesh
        endpoint_mesh_name = "endpoints_" + str(spine.name)
        obj = bpy.data.objects.new(endpoint_mesh_name, endpoint_mesh)

        #Put the endpoint mesh into the same folder as its spine
        collection = bpy.context.scene.collection.children.get(spine.name)
        if not collection:
            pass
        else:
            collection.objects.link(obj)
                            
        verts = [spine_base, spine_tip]

        endpoint_mesh.from_pydata(verts, [], [])
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(True)
    return {'FINISHED'}          


def get_key_with_largest_value(dictionary):
    return max(dictionary, key=lambda k: dictionary[k])


#This class is used to make endpoints for spines that weren't automatically segmented
    #Assumes a single selected spine in edit mode with one/some verts selected
    #Get selected vertex/verticies, find their center and turn them into a vector called "Spine Base"
    #Compare Spine base with other vertices to find Spine Tip at the maximum distance from Spine Base
    #Create Spine base and Tip in the collection of the original spine mesh

class ManualLength(bpy.types.Operator):
    bl_idname = 'object.individual_length_finder' #operators must follow the naming convention of object.lowercase_letters
    bl_label = 'Manual Length'

    def execute(self, context):
        spine_name = name_spine_after_slicer(self)
        vert_list = FindSelectedVerts(self)
        spine_base = FindSpineBase(self, vert_list)
        spine_tip = FindSpineTip(self, spine_base)
        spine_to_collection(self)
        CreateEndpointMesh(self, spine_base, spine_tip, spine_name)
        return {'FINISHED'}

#Get selected verticies
def FindSelectedVerts(self):
    mode = bpy.context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    vert_list = []
    for v in bpy.context.active_object.data.vertices:
        if v.select:
            vert_list.append(v)
        else:
            pass
    
    bpy.ops.object.mode_set(mode=mode)
    return(vert_list)

#Given several selected verticies find the center
def FindSpineBase(self,vert_list):  #TODO: rename to tip
    x, y, z = [ sum( [v.co[i] for v in vert_list] ) for i in range(3)] #Tested this - it does need to be 3
    count = float(len(vert_list))
    spine_base = Vector( (x, y, z ) ) / count        

    return(spine_base)

#Compare the distance between the spine base and all other verices to find the farthest point
def FindSpineTip(self, spine_base):
    spine_length_dict = {}
    spine_coordinates_dict = {}
    obj = bpy.context.active_object


    if obj.name[:6]== 'Stubby':
        ray_direction = obj.location
        ray_max_distance = 10
        hit, location, normal, face_index = obj.ray_cast(spine_base, ray_direction, distance = ray_max_distance)
        spine_tip = location   

    
        #Mark the tip
        bpy.ops.mesh.primitive_ico_sphere_add(radius=.01, calc_uvs=True, enter_editmode=False, align='WORLD', location=(spine_tip), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0)) 
        return(spine_tip)

    else:         
        for vert in bpy.context.active_object.data.vertices:
            length = math.dist(vert.co, spine_base)         
            spine_length_dict[vert.index] = length
            spine_coordinates_dict[vert.index] = vert.co                

            spine_tip_index = max(spine_length_dict, key=spine_length_dict.get)
            spine_tip = spine_coordinates_dict[spine_tip_index]

        #Mark the tip
        bpy.ops.mesh.primitive_ico_sphere_add(radius=.01, calc_uvs=True, enter_editmode=False, align='WORLD', location=(spine_tip), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0)) 

        return(spine_tip)

def CreateEndpointMesh(self, spine_base, spine_tip, spine_name):
    #Use the spine base and spine tip coordinates to create points in active object's collection
    #Get active object
    #obj = bpy.data.objects.get(spine_name)
    obj = bpy.data.objects[spine_name]
    
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

def name_spine_after_slicer(self):
    # Get the selected object
    selected_obj = bpy.context.object
    # Initialize variables for tracking the closest mesh
    closest_distance = float('inf')
    closest_mesh = None

    # Iterate over all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object is a mesh and not the selected object
        if obj.type == 'MESH' and obj != selected_obj and obj.name != "Object":
            # Get the world space positions of the objects
            selected_obj_world = selected_obj.matrix_world.translation
            obj_world = obj.matrix_world.translation

            # Calculate the distance between the objects
            distance = (selected_obj_world - obj_world).length

            # Update the closest mesh if the distance is smaller
            if distance < closest_distance:
                closest_distance = distance
                closest_mesh = obj
    selected_obj.name = closest_mesh.name[6:]
    spine_name = selected_obj.name 
    return(spine_name)


def spine_to_collection(self):    
    spine = bpy.context.object
    old_collection_name = spine.users_collection
    old_collection_name = old_collection_name[0]
    old_collection_name.objects.unlink(spine)
    new_collection_name = spine.name
    new_collection = bpy.data.collections.new(new_collection_name)
    bpy.context.scene.collection.children.link(new_collection)
    new_collection.objects.link(spine)
    return {'FINISHED'}

def cone_raycast(self, spine_base, obj):
    direction = obj.location - spine_base 
    cone_angle = 5
    cone_length = 5
    num_rays = 10
    
    ray_cast_results = []

    obj_matrix = obj.matrix_world

    for i in range(num_rays):
        # Calculate the cone direction for each ray
        angle_offset = math.radians(cone_angle) * (i / (num_rays - 1) - 0.5)
        cone_direction = mathutils.Vector(direction)
        cone_direction.rotate(mathutils.Euler((angle_offset, 0, 0), 'XYZ'))

        # Calculate the start and end points of the ray
        start_point = obj_matrix.inverted() @ spine_base
        end_point = obj_matrix.inverted() @ (spine_base + cone_direction.normalized() * cone_length)

        _, hit_point, _, _ = obj.ray_cast(start_point, end_point - start_point)

        if hit_point is not None:
            # Transform the hit point to world coordinates
            #hit_point = obj_matrix.inverted() @ hit_point
            ray_cast_results.append((hit_point))
    return(ray_cast_results)

# #Add spheres for Check Booleans
# class AddSpheres(bpy.types.Operator):
#     bl_idname = 'object.add_spheres' #operators must follow the naming convention of object.lowercase_letters
#     bl_label = 'Add Spheres'
    
#     def execute(self, context):
#         # Create two icospheres
#         bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 0))
#         sphere1 = bpy.context.object
#         bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 3))
#         sphere2 = bpy.context.object

#         # Rename the icospheres
#         sphere1.name = "BoolSphere1"
#         sphere2.name = "BoolSphere2"

#         return {'FINISHED'}


#Might be useful later

# def paint_spines(self, modified_spine_and_slicer_dict):
#     for spine, slicer in modified_spine_and_slicer_dict.items():
#         slicer = bpy.data.objects.get(slicer)
#         spine = bpy.data.objects.get(spine)

#         if slicer and spine:
#             if slicer.data.materials:
#                 slicer_color = slicer.data.materials[0]

#                 if spine.data.materials:
#                     spine.data.materials[0] = slicer_color
#                 else:
#                     spine.data.materials.append(slicer_color)  

# def mesh_cleaner(self):
#     scene = bpy.context.scene
#     print('cleaning meshes')
#     # Iterate through the objects in the scene collection
#     for obj in scene.collection.all_objects:
#         if obj.type == 'MESH':
#             print(obj.name)
#             bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
#             bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
#             # Switch to Edit Mode
#             bpy.context.view_layer.objects.active
#             bpy.ops.object.mode_set(mode='EDIT')

#             # Select all vertices
#             bpy.ops.mesh.select_all(action='SELECT')
#             #bpy.ops.mesh.remove_doubles()
#             # Recalculate normals
#             bpy.ops.mesh.normals_make_consistent(inside=False)

#             # Switch back to Object Mode
#             bpy.ops.object.mode_set(mode='OBJECT')


