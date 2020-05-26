#New comment here
import bpy
#import pynwb


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
        row.prop(context.scene, "subject_ID")
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
        #subject_ID = bpy.context.scene.subject_ID 
        print('ping')
        return {'FINISHED'}
