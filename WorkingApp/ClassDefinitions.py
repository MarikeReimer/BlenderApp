#New comment here
import bpy
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import Subject

#Create a 3Dview panel and add a row to it
class NeuronAnalysis(bpy.types.Panel):
    bl_label = "Neuron Analysis"
    bl_idname = "PT_TestPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NeuronAnalysis'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator('object.exploding_bits', text = 'Separate Dendrites', icon = 'CUBE')
        row = layout.row()
        row.operator('object.write_nwb', text = "Write NWB File")

        row = self.layout.column(align = True)
        #Subject Table:
        row.prop(context.scene, "subject_id")
        row.prop(context.scene, "age")
        row.prop(context.scene, "subject_description")
        row.prop(context.scene, "genotype")
        row.prop(context.scene, "sex")
        row.prop(context.scene, "species")
        #NWBFile
        row.prop(context.scene, "identifier")
        row.prop(context.scene, "session_start_time")
        row.prop(context.scene, "session_description")




#Row operator for panel that applies "separate by loose parts" to mesh    
class ExplodingBits(bpy.types.Operator):
    bl_idname = 'object.exploding_bits'
    bl_label = 'Exploding Bits'
    
    def execute(self, context):
        #Select ative object
        object = bpy.context.active_object
        #Split it into pieces
        bpy.ops.mesh.separate(type='LOOSE')
        return {'FINISHED'}

#Row operator for writing NWB file
class WriteNWB(bpy.types.Operator):
    bl_idname = 'object.write_nwb'
    bl_label = 'Write NWB File'

    def execute(self, context):
        subject_id = bpy.context.scene.subject_id 
        age = bpy.context.scene.age
        subject_description = bpy.context.scene.subject_description
        genotype = bpy.context.scene.genotype
        sex = bpy.context.scene.sex
        species = bpy.context.scene.species
        identifier = bpy.context.scene.identifier
        #session_start_time = datetime(bpy.context.scene.session_start_time.tolist())  #Will need to do string manipulations of some sort to get this working
        session_description = bpy.context.scene.session_description

        nwbfile_name = identifier + '.nwb'

        nwbfile = NWBFile(session_description = session_description,
            identifier = identifier, 
            session_start_time = datetime.now(),  #Fix this
            file_create_date = datetime.now())  

        subject = Subject(
            description = subject_description,
            genotype = genotype,
            sex = sex,
            species = species,
            subject_id = subject_id,
            )

        with NWBHDF5IO(nwbfile_name, 'w') as io:
            io.write(nwbfile)

        return {'FINISHED'}
