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

        row = self.layout.column(align = True)
        row.prop(context.scene, "subject_ID")
        row.prop(context.scene, "age")
        row.prop(context.scene, "subject_description")
        row.prop(context.scene, "genotype")
        row.prop(context.scene, "sex")
        row.prop(context.scene, "species")
        



#Row operator for panel that applies "separate by loose parts" to mesh    
class ExplodingBits(bpy.types.Operator):
    bl_idname = 'object.exploding_bits'
    bl_label = 'Exploding Bits'
    
    def execute(self, context):
        #Select ative object
        object = bpy.context.active_object
        #Split it into pi
        bpy.ops.mesh.separate(type='LOOSE')
        return {'FINISHED'}