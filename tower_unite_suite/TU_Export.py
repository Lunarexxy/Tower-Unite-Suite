# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import os, sys, shutil, bpy, re
from contextlib import suppress
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty, FloatProperty
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector
from datetime import datetime
import bpy.utils.previews

from tower_unite_suite.TU_Armature import Verify_TU_Armature as Verify_TU_Armature, TU_Bone_Names as TU_Bone_Names
from tower_unite_suite.TU_Rig_Data import TU_Bone_Names as TU_Bone_Names, Twist_Bones as Twist_Bones, Finger_Bones_L as Finger_Bones_L, Finger_Bones_R as Finger_Bones_R
from tower_unite_suite.Tower_Icons import TU_Icons as TU_Icons

addon_version = "unknown"
def get_addon_version():
    # this is set in __init__
    return addon_version

def gamma(c):
    if c < 0.0031308:
        return 0.0 if c < 0.0 else c * 12.92
    else:
        return 1.055 * pow(c, 1.0 / 2.4) - 0.055

def write_log(file, line):
    if not file == None:
        file.write(datetime.now().strftime("\n[%Y/%m/%d %H:%M:%S.%f] ") + line)

def get_root_node(Base_Node, Target, NodeIndex = 0):
    Input = Base_Node.inputs[Target]
    if not Input:
        return None
    if len(Input.links) <= NodeIndex:
        return None
    Link = Input.links[NodeIndex]
    if not Link:
        return None
    Node = Link.from_node
    if not Node:
        return None
    return Node
        
UsedIDs = []
def IdentifyID(input):
    input = input.replace('.', '_')
    for i in range(10):
        if input[0] == str(i):
            input = '_' + input[1:]
            testInput = input
            index = 1
            for j in UsedIDs:
                if j == testInput:
                    index += 1
                    testInput = input + str(index)
            UsedIDs.append(testInput)
            return testInput
    return input

class TU_Image_Data:
    Image = None
    Image_Name = ""
    Image_Filename = ""
    Image_ID = ""
    Image_Surface = ""
    Image_Sampler = ""
    Owner_ID = ""
    Owner_Effect = ""
    
    @staticmethod
    def strip(str):
        return re.sub('[ \(\)]', '_', str)
    
    def __init__(self, img, usr):
        self.Image = img
        self.Image_Name = img.name_full
        self.Image_Filename = bpy.path.basename(img.filepath)
        self.Image_ID = self.strip(self.Image_Name)
        self.Image_Surface = self.Image_ID + '-surface'
        self.Image_Sampler = self.Image_ID + '-sampler'
        self.Owner_ID = IdentifyID(usr.name)
        self.Owner_Effect = self.strip(self.Owner_ID) + '-effect'

class TU_Export_Collada(Operator, ExportHelper):
    """Export to Tower Unite's specifications"""
    bl_idname = "tower_unite_suite.export"
    bl_label = "Export Tower Unite Model"
    bl_options = {"PRESET"}
    bl_space_type = 'FILE_BROWSER'
    
    filename_ext = ".dae"
    filter_glob : StringProperty(default="*.dae", options={"HIDDEN"})
    
    use_triangles : BoolProperty(
        name="Triangulate",
        description="Export Polgyons (Quads & NGons) as Triangles (results are varied; toggle if Tower Unite showed holes in the model)",
        default=False,
    )
    
    use_copy_images : BoolProperty(
        name="Copy Textures (recommended)",
        description="Copy textures to same folder where the .dae file is exported",
        default=True,
        )
    
    archive_old_exports : BoolProperty(
        name="Archive instead of overwriting",
        description="Instead of overwriting a file, the original will be renamed",
        default=True,
        )
    
    debug_log : BoolProperty(
        name="Export log (debug)",
        description="Steps will be logged and recorded to a file for debugging problems with your export",
        default=False,
        )
    
    pre_process : BoolProperty(
        name="Magic Export (recommended)",
        description="Magic Export will prevent many common errors and includes many quality of life features",
        default=True,
        )
    
    pp_help: BoolProperty(
        name='',
        description='Show help text',
        default=False,
        )
        
    pp_clavicle_values=[
        ('NONE', 'Clavicles (untouched)', 'Do not re-weight the clavicles', 'IPO_LINEAR', 1),
        ('ARMS', 'Arms', 'Re-weight the clavicles to the upperarm bones', 'IPO_CONSTANT', 2),
        ('SPINE1', 'Spine_01', 'Merge the clavicles with spine_01', 'IPO_SINE', 3),
        ('SPINE2', 'Spine_02', 'Merge the clavicles with spine_02', 'IPO_QUAD', 4),
        ('SPINE3', 'Spine_03', 'Merge the clavicles with spine_03', 'IPO_CUBIC', 5),
    ]
    pp_clavicle: EnumProperty(
        items=pp_clavicle_values,
        name='',
        description='Re-weight the clavicles to a different bone',
        default='NONE',
        )
    
    pp_help_clavicle: BoolProperty(
        name='',
        description='Show help text',
        default=False,
        )
    
    pp_twist: BoolProperty(
        name='Purge twist bones',
        description='Shift all weights from twist bones to their counterparts',
        default=True,
        )
    
    pp_help_twist: BoolProperty(
        name='',
        description='Show help text',
        default=False,
        )
    
    pp_fingers: FloatProperty(
        name='Finger strength',
        description='How much finger weights should be kept. Values closer to 0% shift some of the weight to the hands instead',
        default=100,
        min=0.0,
        max=100,
        soft_min=0.0,
        soft_max=100,
        precision=0,
        step=1,
        subtype='PERCENTAGE',
        )
    
    pp_help_fingers: BoolProperty(
        name='',
        description='Show help text',
        default=False,
        )
    
    pp_visible: BoolProperty(
        name='Ignore hidden meshes',
        description='Do not export meshes which are not visible in the scene',
        default=True,
        )
    
    pp_help_visible: BoolProperty(
        name='',
        description='Show help text',
        default=False,
        )
    
    @staticmethod
    def infobox(layout, strings):
        info = layout.row()
        col = info.column()
        col.label(icon='INFO')
        col = info.column()
        for str in strings:
            row = col.row()
            row.label(text=str)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(icon='MARKER_HLT' if self.use_triangles else 'MARKER')
        row.prop(self, 'use_triangles')
        
        row = layout.row()
        row.label(icon='NODE_COMPOSITING' if self.use_copy_images else 'FILE_IMAGE')
        row.prop(self, 'use_copy_images')
        
        row = layout.row()
        row.label(icon='OUTLINER_OB_GROUP_INSTANCE' if self.archive_old_exports else 'OUTLINER_COLLECTION')
        row.prop(self, 'archive_old_exports')
        
        row = layout.row()
        row.label(icon='RESTRICT_VIEW_OFF' if self.debug_log else 'RESTRICT_VIEW_ON')
        row.prop(self, 'debug_log')
        
        row = layout.row()
        row.separator()
        
        row = layout.row()
        split = row.split(factor=0.9)
        split.prop(self, 'pre_process', icon='SHADERFX')
        split.prop(self, 'pp_help', icon='QUESTION')
        if self.pre_process:
            if self.pp_help:
                self.infobox(layout, [
                    'This puts your model through some',
                    'extra steps before exporting, without',
                    'making any changes to your model.',
                    'It allows the use of simple colours for',
                    'materials, processes modifiers and',
                    'adds an Armature modifier for you.',
                    'Additionally, see the options below:',
                ])
            
            row = layout.row()
            row.separator()
            
            row = layout.row()
            row.label(icon='VIS_SEL_10' if self.pp_visible else 'VIS_SEL_11')
            split = row.split(factor=0.88)
            split.prop(self, 'pp_visible')
            split.prop(self, 'pp_help_visible', icon='QUESTION')
            if self.pp_help_visible:
                self.infobox(layout, [
                    'If checked, this option will only export',
                    'mesh objects that are visible in the',
                    'current scene. If NOT checked, hidden',
                    'mesh objects will be exported too.',
                ])
            
            row = layout.row()
            row.separator()
            
            row = layout.row()
            row.label(icon='BONE_DATA' if self.pp_twist else 'GROUP_BONE')
            split = row.split(factor=0.88)
            split.prop(self, 'pp_twist')
            split.prop(self, 'pp_help_twist', icon='QUESTION')
            if self.pp_help_twist:
                self.infobox(layout, [
                    'This transfers bone weights from twist',
                    'bones to their counterparts.',
                ])
                
            row = layout.row()
            row.separator()
            
            row = layout.row()
            split = row.split(factor=0.9)
            split.label(text='Re-assign clavicle weights to:')
            split.prop(self, 'pp_help_clavicle', icon='QUESTION')
            
            row = layout.row()
            row.prop(self, 'pp_clavicle')
            if self.pp_help_clavicle:
                self.infobox(layout, [
                    'This option transfers bone weights',
                    'from the clavicle to the chosen area.',
                ])
            
            row = layout.row()
            row.separator()
            
            row = layout.row()
            split = row.split(factor=0.9)
            split.prop(self, 'pp_fingers')
            split.prop(self, 'pp_help_fingers', icon='QUESTION')
            if self.pp_help_fingers:
                self.infobox(layout, [
                    'Weakening the finger strength will',
                    'transfer some weight to the hand',
                    'and relax the \'sawtooth effect\'.',
                ])
        elif self.pp_help:
            self.infobox(layout, [
                'This puts your model through some',
                'extra steps before exporting, without',
                'making any changes to your model.',
                'It allows the use of simple colours for',
                'materials, processes modifiers and',
                'adds an Armature modifier for you.',
                'There are also additional options.'
            ])
    
    def execute(self, context):
        if not self.filepath:
            raise Exception("Filepath not set")
        
        TU_Log_File = None
        if self.debug_log:
            TU_Log_File = open(self.filepath[:-4] + "_log.txt", 'wt')
            
            # Log Header
            TU_Log_File.write("Tower Unite Suite " + get_addon_version() + " by Spoom :: Running on Blender " + bpy.app.version_string + "\nExport log for '" + os.path.basename(os.path.realpath(self.filepath)) +"'")
            if self.pre_process:
                TU_Log_File.write("\nMagic Export enabled")
                Nothing = True
                if self.use_triangles:
                    TU_Log_File.write("\n Triangulate spell requested.")
                    Nothing = False
                if self.use_copy_images:
                    TU_Log_File.write("\n Textures will be copied by a mime.")
                    Nothing = False
                if self.archive_old_exports:
                    if os.path.exists(self.filepath):
                        TU_Log_File.write("\n The previous export will be spirited away to the archives.")
                        Nothing = False
                if self.pp_visible:
                    TU_Log_File.write("\n The invisible man may make an appearance... or will he?")
                    Nothing = False
                if self.pp_twist:
                    TU_Log_File.write("\n Twist Bones volunteered for disappearing act.")
                    Nothing = False
                if not self.pp_clavicle == 'NONE':
                    TU_Log_File.write("\n See Clavicle the escape artist dislocate his shoulders.")
                    Nothing = False
                if self.pp_fingers:
                    if Nothing:
                        TU_Log_File.write("\n Sadly, we could only afford Uncle Donny and his 'trick' where he pretends to pull his fingers off.")
                    else:
                        TU_Log_File.write("\n We also promised Uncle Donny could do that 'trick' where he pretends to pull his fingers off.")
                        Nothing = False
                    if self.pp_fingers < 100:
                        TU_Log_File.write(" (" + str(round(self.pp_fingers)) + "% of kids approve)")
                    else:
                        TU_Log_File.write(" ")
                if Nothing:
                    TU_Log_File.write("\n Just the standard show tonight. Nothing fancy.")

            else:
                TU_Log_File.write("\nMagic Export disabled")
                if self.use_triangles:
                    TU_Log_File.write("\n Triangulate: on")
                else:
                    TU_Log_File.write("\n Triangulate: off")
                if self.use_copy_images:
                    TU_Log_File.write("\n Copy textures: on")
                else:
                    TU_Log_File.write("\n Copy textures: off")
                if self.archive_old_exports:
                    if os.path.exists(self.filepath):
                        TU_Log_File.write("\n Archive: on")
                    else:
                        TU_Log_File.write("\n Archive: unnecessary")
                else:
                    TU_Log_File.write("\n Archive: off")
        
        if len(bpy.data.meshes) == 0:
            write_log(TU_Log_File, "ERROR: Tower Unite exports require at least one mesh.")
            raise Exception("Tower Unite exports require at least one mesh")
            
        if self.pre_process:
            try:
                write_log(TU_Log_File, "Starting the magic show.")
                old_scene = bpy.context.window.scene # Store the old scene
                old_view_layer = bpy.context.view_layer # To check visibility
                process_scene = bpy.data.scenes.new('TU_Export') # New scene
                bpy.context.window.scene = process_scene # Switch to new scene
                write_log(TU_Log_File, "Finished setting up the stage.")
                duplicated_objects = []
                duplicated_meshes = []
                duplicated_materials = {} # Must be indexed by name
                rgb_images = {}
                
                stats_mods_applied = 0
                stats_mods_removed = 0
                stats_bones_mirrored = 0
                stats_bones_removed = 0
                stats_pixels_made = 0
                
                write_log(TU_Log_File, "Looking for an actor.")
                TU_Armature = None
                if 'Armature' in old_scene.objects:
                    TU_Armature = old_scene.objects['Armature']
                    if Verify_TU_Armature(TU_Armature): # This checks object type, bone count and bone type
                        process_scene.collection.objects.link(TU_Armature) # Link the Armature to the new scene
                        write_log(TU_Log_File, "Found an actor: '" + TU_Armature.data.name_full + "'")
                    else: # Why would you try to fool me like this?
                        TU_Armature = None
                        write_log(TU_Log_File, "Thought we found an actor, but it was just '" + TU_Armature.data.name_full + "'...")
                else:
                    write_log(TU_Log_File, "Couldn't find an actor. Guess this is a furniture item.")
                
                other_reason = False
                if not self.pp_clavicle == 'NONE':
                    other_reason = True
                    if self.pp_clavicle == 'ARMS':
                        pp_clavicle_mix = {'clavicle_l': 'upperarm_l', 'clavicle_r': 'upperarm_r'}
                    elif self.pp_clavicle == 'SPINE1':
                        pp_clavicle_mix = {'clavicle_l': 'spine_01', 'clavicle_r': 'spine_01'}
                    elif self.pp_clavicle == 'SPINE2':
                        pp_clavicle_mix = {'clavicle_l': 'spine_02', 'clavicle_r': 'spine_02'}
                    elif self.pp_clavicle == 'SPINE3':
                        pp_clavicle_mix = {'clavicle_l': 'spine_03', 'clavicle_r': 'spine_03'}
                
                if self.pp_fingers < 100:
                    other_reason = True
                    finger_strength = self.pp_fingers / 100
                
                if self.pp_twist:
                    other_reason = True
                
                for obj in old_scene.objects: # Loop through all the old objects
                    if not obj.type == 'MESH': continue
                    
                    if self.pp_visible:
                        if obj.hide_get(view_layer=old_view_layer):
                            write_log(TU_Log_File, "Mesh '" + obj.name + "' hid from our agents and will not appear in the show.")
                            continue
                    
                    write_log(TU_Log_File, "Checking mesh '" + obj.name + "'")
                    
                    new_obj = obj.copy() # Make and link a copy of the object to the new scene
                    new_obj.name = 'MAGIC-' + obj.name#.replace('_','-')
                    duplicated_objects.append(new_obj)
                    process_scene.collection.objects.link(new_obj)
                    
                    has_modifiers = True if len(obj.modifiers) > 0 else False
                    single_col = False
                    
                    write_log(TU_Log_File, " Checking materials for RGB values...")
                    for mat in obj.data.materials:
                        if not 'Material Output' in mat.node_tree.nodes:
                            write_log(TU_Log_File, "   Material '" + mat.name + "' is blank, not even a Material Output! You should probably delete it.")
                            continue
                        mat_out = mat.node_tree.nodes['Material Output']
                        if not mat_out:
                            write_log(TU_Log_File, "   Material '" + mat.name + "' is broken, something is up with the Material Output! You should probably check that out.")
                            continue
                        bsdf = get_root_node(mat_out, 'Surface')
                        if not bsdf:
                            write_log(TU_Log_File, "   Material '" + mat.name + "' is blank, not even a Surface node! You should probably check that.")
                            continue
                        if not bsdf.type == 'BSDF_PRINCIPLED':
                            write_log(TU_Log_File, "   Material '" + mat.name + "' isn't a Principled BSDF. I'm not paid enough to work with '" + bsdf.type + "' and neither is Tower Unite.")
                            continue
                        
                        Base = bsdf.inputs['Base Color']
                        if len(Base.links) == 0: # Using default value, so an image must be created
                            single_col = True
                            if self.debug_log:
                                continue # So we can yell at you for the others!
                            else:
                                break # No need. We're only determining if we need to create single-pixel RGB texture images.
                    
                    if single_col:
                        write_log(TU_Log_File, " Finished checking materials. We'll have to work some magic with those RGB values.")
                    else:
                        write_log(TU_Log_File, " Finished checking materials. Everything has a texture; no magic needed here.")
                    
                    extra_vgs = False
                    for vg in obj.vertex_groups.keys():
                        if not vg in TU_Bone_Names:
                            extra_vgs = True
                            break
                    
                    if extra_vgs:
                        write_log(TU_Log_File, " Finished checking vertex groups. We'll need a vanishing act.")
                    else:
                        write_log(TU_Log_File, " Finished checking vertex groups. All is well; no magic needed here.")
                    
                    if single_col or has_modifiers or extra_vgs or other_reason: # Mesh must be duplicated and processed
                        write_log(TU_Log_File, " We need to copy this mesh to work on it.")
                        new_mesh = obj.data.copy()
                        new_obj.data = new_mesh
                        duplicated_meshes.append(new_mesh)
                        bpy.context.view_layer.objects.active = new_obj # Necessary to stop stuff crashing later on
                        
                        if extra_vgs:
                            write_log(TU_Log_File, " Vanish, rogue vertex groups:")
                            for name,group in new_obj.vertex_groups.items():
                                if not name in TU_Bone_Names:
                                    write_log(TU_Log_File, "  '"+ name +"'")
                                    new_obj.vertex_groups.remove(group)
                                    stats_bones_removed += 1
                            write_log(TU_Log_File, " Tower Unite won't yell at you for that now, but do check your vertex groups.")
                        
                        keys = new_obj.vertex_groups.keys()
                        
                        if not self.pp_clavicle == 'NONE':
                            write_log(TU_Log_File, " Time for Clavicle's escape act.")
                            for k,v in pp_clavicle_mix.items():
                                if k in keys:
                                    if not v in keys:
                                        new_obj.vertex_groups.new(name = v)
                                    pp_mod = new_obj.modifiers.new(name='TU_PP_Clavicle_Mix', type='VERTEX_WEIGHT_MIX')
                                    pp_mod.vertex_group_a = v
                                    pp_mod.vertex_group_b = k
                                    pp_mod.mix_mode = 'ADD'
                                    bpy.ops.object.modifier_apply(modifier = pp_mod.name)
                                    new_obj.vertex_groups.remove(new_obj.vertex_groups[k])
                        
                        if self.pp_twist:
                            write_log(TU_Log_File, " Twist bones? What Twist bones? ALAKAZAM!")
                            for twist,counterpart in Twist_Bones.items():
                                if twist in keys:
                                    if not counterpart in keys:
                                        new_obj.vertex_groups.new(name = counterpart)
                                    pp_mod = new_obj.modifiers.new(name='TU_PP_Twist', type='VERTEX_WEIGHT_MIX')
                                    pp_mod.vertex_group_a = counterpart
                                    pp_mod.vertex_group_b = twist
                                    pp_mod.mix_mode = 'ADD'
                                    bpy.ops.object.modifier_apply(modifier = pp_mod.name)
                                    new_obj.vertex_groups.remove(new_obj.vertex_groups[twist])
                                    stats_bones_removed += 1
                        
                        if self.pp_fingers < 100:
                            write_log(TU_Log_File, " Uncle Donny is up. Please just pretend you're impressed; he needs this.")
                            for hand, fingers in {'hand_l': Finger_Bones_L, 'hand_r': Finger_Bones_R}.items():
                                if not hand in keys:
                                    new_obj.vertex_groups.new(name = hand)
                                for finger in fingers:
                                    if not finger in keys:
                                        continue
                                    pp_mod = new_obj.modifiers.new(name='TU_PP_Finger_To_Hand', type='VERTEX_WEIGHT_MIX')
                                    pp_mod.vertex_group_a = hand
                                    pp_mod.vertex_group_b = finger
                                    pp_mod.mix_mode = 'ADD'
                                    pp_mod.mask_constant = finger_strength
                                    bpy.ops.object.modifier_apply(modifier = pp_mod.name)
                                    if finger_strength > 0:
                                        pp_mod = new_obj.modifiers.new(name='TU_PP_Finger_Sub', type='VERTEX_WEIGHT_MIX')
                                        pp_mod.vertex_group_a = finger
                                        pp_mod.vertex_group_b = finger
                                        pp_mod.mix_set = 'A'
                                        pp_mod.mix_mode = 'SUB'
                                        pp_mod.mask_constant = finger_strength
                                        bpy.ops.object.modifier_apply(modifier = pp_mod.name)
                                    else:
                                        new_obj.vertex_groups.remove(new_obj.vertex_groups[finger])
                                        stats_bones_removed += 1

                        if has_modifiers:
                            for mod in new_obj.modifiers:
                                if mod.type == 'MIRROR':
                                    write_log(TU_Log_File, "  Oh hey, a magic mirror! I'll make sure you have vertex groups for both sides.")
                                    missing_vgs = [] # Create any missing mirrored bones before applying
                                    for vg in keys:
                                        check = vg[-2:]
                                        if check == "_l":
                                            check = vg[:-2] + "_r"
                                        elif check == "_r":
                                            check = vg[:-2] + "_l"
                                        else:
                                            continue
                                        if not check in new_obj.vertex_groups:
                                            missing_vgs.append(check)
                                            stats_bones_mirrored += 1
                                    for vg in missing_vgs:
                                        new_obj.vertex_groups.new(name = vg)
                                        write_log(TU_Log_File, "   '" + vg + "'")
                                    write_log(TU_Log_File, "  You're welcome!")
    #                            try:
    #                                bpy.ops.object.modifier_apply(modifier = mod.name)
    #                            except:
    #                                new_obj.modifiers.remove(mod)
    #                        
    #                       DO NOT OPTIMISE LIKE THE ABOVE COMMENTS!
    #                       The changes above have no effect if the modifiers are applied in the same loop.
    #                       It's the exact same loop context and I have no idea why the above doesn't work. Too bad!
                            write_log(TU_Log_File, " For this next trick I will APPLY some MODIFIERS. Amazing.")
                            for mod in new_obj.modifiers:
                                try:
                                    write_log(TU_Log_File, "  " + mod.type + " '" + mod.name + "'...")
                                    bpy.ops.object.modifier_apply(modifier = mod.name)
                                    stats_mods_applied += 1
                                    write_log(TU_Log_File, "  ...APPLIED!")
                                except RuntimeError:
                                    new_obj.modifiers.remove(mod)
                                    stats_mods_removed += 1
                                    write_log(TU_Log_File, "  ...DELETED!")
                                except Exception as err:
                                    write_log(TU_Log_File, "  ...I tried, okay? Hit with a '" + str(type(err)) + "'... We'll have to do without '" + mod.name + "'.")
                                    new_obj.modifiers.remove(mod)
                                    stats_mods_removed += 1
                        
                        if single_col:
                            write_log(TU_Log_File, " Pixels, pixels, pixels. Who needs textures? I'll make them for you.")
                            for i in range(len(new_mesh.materials)): # need indexer for reassignment
                                mat = new_mesh.materials[i]
                                if not mat: # For some reason, this can pick up NoneTypes
                                    continue
                                if mat.name in duplicated_materials:
                                    new_mesh.materials[i] = duplicated_materials[mat.name]
                                    continue
                                
                                if not 'Material Output' in mat.node_tree.nodes:
                                    continue
                                mat_out = mat.node_tree.nodes['Material Output']
                                if not mat_out:
                                    continue
                                bsdf = get_root_node(mat_out, 'Surface')
                                if not bsdf:
                                    continue
                                if not bsdf.type == 'BSDF_PRINCIPLED':
                                    continue
                                
                                Base = bsdf.inputs['Base Color']
                                if len(Base.links) > 0:
                                    continue
                                
                                write_log(TU_Log_File, "  Here's one for '" + mat.name + "'.")
                                new_mat = mat.copy() # Work on a copy of the material
                                new_mat.name = mat.name + ' (Pixel)'
                                new_mesh.materials[i] = new_mat
                                duplicated_materials[mat.name] = new_mat
                                
                                Base = get_root_node(new_mat.node_tree.nodes['Material Output'], 'Surface').inputs['Base Color']
                                
                                material_rgba = Base.default_value
                                for c in range(4): # Gamma correction
                                    material_rgba[c] = gamma(material_rgba[c])
                                image_name = 'Pixel_' + str(int(material_rgba[0]*255.0)) + '-' + str(int(material_rgba[1]*255.0)) + '-' + str(int(material_rgba[2]*255.0)) + '-' + str(int(material_rgba[3]*255.0))
                                if image_name in rgb_images:
                                    rgb_img = rgb_images[image_name]
                                    write_log(TU_Log_File, "   I already gave you a " + image_name + ". Don't be greedy.")
                                else:
                                    rgb_img = bpy.data.images.new(image_name, 1, 1, alpha=True)
                                    rgb_images[image_name] = rgb_img
                                    rgb_img.pixels = [material_rgba[0], material_rgba[1], material_rgba[2], material_rgba[3]]
                                    stats_pixels_made += 1
                                    write_log(TU_Log_File, "   Abracadabra! Your very own " + image_name + ".")
                                    
                                img_node = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
                                img_node.image = rgb_img
                                new_mat.node_tree.links.new(img_node.outputs['Color'], Base)

                    if TU_Armature: # Playermodel
                        write_log(TU_Log_File, " We're all done. Let's put it back on the armature.")
                        arm_mod = new_obj.modifiers.new('Armature', 'ARMATURE')
                        arm_mod.object = TU_Armature
                        
                        write_log(TU_Log_File, " And finally: apply transforms.")
                    try:
                        new_obj.select_set(True)
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
                        new_obj.select_set(False)
                    except:
                        write_log(TU_Log_File, "  Transform your expectations, because it didn't work.")
                        print("Unable to apply all transforms for object '" + obj.name_full + "'")
                        continue
            except:
                write_log(TU_Log_File, "WHOA! Something exploded or something. I don't know what. Let's clean up this mess...")
                bpy.context.window.scene = old_scene # Switch to old scene
                bpy.data.scenes.remove(process_scene) # Delete new scene and clean up
                for x in duplicated_objects:
                    write_log(TU_Log_File, " Cleaning object '" + x.name_full + "'")
                    bpy.data.objects.remove(x)
                for x in duplicated_meshes:
                    write_log(TU_Log_File, " Cleaning mesh '" + x.name_full + "'")
                    bpy.data.meshes.remove(x)
                for x in duplicated_materials:
                    write_log(TU_Log_File, " Cleaning material '" + x.name_full + "'")
                    bpy.data.materials.remove(duplicated_materials[x])
                for x in rgb_images:
                    write_log(TU_Log_File, " Cleaning image '" + x + "'")
                    bpy.data.images.remove(rgb_images[x])
                process_scene = None # So we know not to delete it a second time.
                write_log(TU_Log_File, "Show's over, I guess.")

        TU_Materials = [] # All active materials
        TU_Images = [] # Images to include
        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                continue
            for mat in mesh.materials:
                if not mat:
                    continue
                if mat.users == 0:
                    continue
                if mat in TU_Materials:
                    continue
                TU_Materials.append(mat)
        UsedIDs.clear()
        write_log(TU_Log_File, "Looking for normal maps.")
        for mat in TU_Materials:
            if not 'Material Output' in mat.node_tree.nodes:
                continue
            if mat.node_tree.users == 0: # Spooky ghost material
                continue
            mat_out = mat.node_tree.nodes['Material Output']
            if not mat_out:
                continue
            bsdf = get_root_node(mat_out, 'Surface')
            if not bsdf:
                continue
            if not bsdf.type == 'BSDF_PRINCIPLED':
                continue
            base_color = get_root_node(bsdf, 'Base Color')
            if not base_color:
                continue
            if not base_color.type == 'TEX_IMAGE':
                continue
            normal_map = get_root_node(bsdf, 'Normal')
            if not normal_map:
                continue
            if not normal_map.type == 'NORMAL_MAP':
                continue
            normal_texture = get_root_node(normal_map, 'Color')
            if not normal_texture:
                continue
            if not normal_texture.type == 'TEX_IMAGE':
                continue
            write_log(TU_Log_File, " '" + mat.name + "' has one.")
            TU_Images.append(TU_Image_Data(normal_texture.image, mat))

        TU_FilePath = self.filepath
        TU_FileName = bpy.path.basename(TU_FilePath)
        TU_FileFolder = TU_FilePath[:-len(TU_FileName)]
        if self.archive_old_exports:
            TU_CheckPath = TU_FilePath
            if os.path.exists(TU_CheckPath):
                TU_FileBackupInteger = 0
                TU_CheckName = TU_FileName[:-4] # Cut off the '.dae'
                while os.path.exists(TU_CheckPath):
                    TU_FileBackupInteger += 1
                    TU_CheckPath = TU_FileFolder + TU_CheckName + "_" + str(TU_FileBackupInteger) + ".dae"
                write_log(TU_Log_File, "Wave goodbye to '" + os.path.basename(os.path.realpath(TU_FilePath)) + "' because it's about to become '" + os.path.basename(os.path.realpath(TU_CheckPath)) + "'! Viola!")
                os.rename(TU_FilePath, TU_CheckPath)
        
        write_log(TU_Log_File, "Starting the export now.")
        bpy.ops.wm.collada_export(
            filepath=TU_FilePath,
            check_existing=False,
            apply_modifiers=False,
            export_mesh_type=0,
            export_mesh_type_selection='view',
            export_global_forward_selection='Y', # Tower Unite setting
            export_global_up_selection='Z', # Tower Unite setting
            apply_global_orientation=False,
            selected=False,
            include_children=True,
            include_armatures=True,
            include_shapekeys=False,
            deform_bones_only=False,
            include_animations=False,
            active_uv_only=True,
            use_texture_copies=self.use_copy_images,
            triangulate=self.use_triangles,
            use_object_instantiation=False,
            use_blender_profile=True,
            sort_by_name=False,
            export_object_transformation_type=0,
            export_object_transformation_type_selection='matrix',
            open_sim=False,
            limit_precision=False,
            keep_bind_info=False
        )

        if self.pre_process:
            print('Pre-processing complete')
            if not process_scene == None:
                write_log(TU_Log_File, "Time to clean up after the magic show.")
                bpy.context.window.scene = old_scene # Switch to old scene
                bpy.data.scenes.remove(process_scene) # Delete new scene and clean up
                for x in duplicated_objects:
                    write_log(TU_Log_File, " Cleaning object '" + x.name_full + "'")
                    bpy.data.objects.remove(x)
                for x in duplicated_meshes:
                    write_log(TU_Log_File, " Cleaning mesh '" + x.name_full + "'")
                    bpy.data.meshes.remove(x)
                for x in duplicated_materials:
                    write_log(TU_Log_File, " Cleaning material '" + x.name_full + "'")
                    bpy.data.materials.remove(duplicated_materials[x])
                for x in rgb_images:
                    write_log(TU_Log_File, " Cleaning image '" + x + "'")
                    bpy.data.images.remove(rgb_images[x])
                write_log(TU_Log_File, "All clean!")
            
            # Stats
            write_log(TU_Log_File, "Let's see what we accomplished:")
            if stats_mods_applied > 0:
                print('- ' + str(stats_mods_applied) + ' modifier(s) applied.')
                write_log(TU_Log_File, " " + str(stats_mods_applied) + ' modifier(s) applied.')
            if stats_mods_removed > 0:
                print('- ' + str(stats_mods_removed) + ' modifier(s) removed.')
                write_log(TU_Log_File, " " + str(stats_mods_removed) + ' modifier(s) removed.')
            if stats_bones_mirrored > 0:
                print('- ' + str(stats_bones_mirrored) + ' bone(s) mirrored.')
                write_log(TU_Log_File, " " + str(stats_bones_mirrored) + ' bone(s) mirrored.')
            if stats_bones_removed > 0:
                print('- ' + str(stats_bones_removed) + ' bone(s) removed.')
                write_log(TU_Log_File, " " + str(stats_bones_removed) + ' bone(s) removed.')
            if stats_pixels_made > 0:
                print('- ' + str(stats_pixels_made) + ' pixel image(s) created.')
                write_log(TU_Log_File, " " + str(stats_pixels_made) + ' pixel image(s) created.')

        if self.use_copy_images:
            if len(TU_Images) > 0:
                printed = False
                TU_Processed = [] # Images already processed
                for img in TU_Images:
                    copy_from = bpy.path.abspath(img.Image.filepath)
                    skip_me = False
                    for check_name in TU_Processed:
                        if check_name == copy_from:
                            skip_me = True
                            break
                    if skip_me:
                        continue
                    TU_Processed.append(copy_from)
                    copy_to = TU_FileFolder + img.Image_Filename
                    if copy_from == copy_to:
                        continue
                    if not printed:
                        printed = True
                        print('Copying images:')
                        write_log(TU_Log_File, "Copying images:")
                    print(copy_from + ' -> ' + copy_to)
                    write_log(TU_Log_File, " " + copy_from + ' -> ' + copy_to)
                    shutil.copy(copy_from, copy_to)
        
        if len(bpy.data.materials) == 0 or len(bpy.data.images) == 0:
            if self.debug_log:
                write_log(TU_Log_File, "We're done here. Good night.")
                TU_Log_File.close()
            return {'FINISHED'}
        
        # Yes, I edit the file after it has been saved. It's hacky, but it works just fine and it's a lot easier to maintain than manually building the export file.
        TU_Save_File = open(TU_FilePath, 'rt')
        TU_File_Content = TU_Save_File.read()
        TU_Save_File.close()
        TU_New_Content = ''

        TU_Index = TU_File_Content.find('</library_images>')
        if TU_Index < 0: # No images means no bumpmap
            if self.debug_log:
                write_log(TU_Log_File, "We're done here. Good night.")
                TU_Log_File.close()
            return {'FINISHED'}
        
        write_log(TU_Log_File, "Now we have to fix the export to include normal maps.")
        TU_New_Content = TU_File_Content[:TU_Index]
        TU_Processed = [] # Images already processed
        for img in TU_Images:
            skip_me = False
            for check_name in TU_Processed:
                if check_name == img.Image_ID:
                    skip_me = True
                    break
            if skip_me:
                continue
            TU_Processed.append(img.Image_ID)
            TU_New_Content += '  <image id="' + img.Image_ID + '" name="' + img.Image_ID + '">\n      <init_from>' + img.Image_Filename + '</init_from>\n    </image>\n  '
            print('Collada post-export: Added image: ' + img.Image_Filename)
            write_log(TU_Log_File, " Added '" + img.Image_Filename + "' to library images.")
        TU_New_Content += TU_File_Content[TU_Index:]
        TU_File_Content = TU_New_Content
        TU_Processed = [] # Images already processed
        for img in TU_Images:
            skip_me = False
            for check_name in TU_Processed:
                if check_name == img.Owner_Effect:
                    skip_me = True
                    break
            if skip_me:
                continue
            TU_Processed.append(img.Owner_Effect)
            
            TU_Index_Start = TU_File_Content.find('<effect id="' + img.Owner_Effect + '">')
            if TU_Index_Start < 0: # why does this happen aaaaaaaaa
                continue
            TU_Index_End = TU_File_Content.index('</effect>', TU_Index_Start)
            TU_Index = TU_Index_Start
            while True:
                index = TU_File_Content.find('</newparam>', TU_Index, TU_Index_End)
                if index == -1:
                    break
                TU_Index = index + 11
            if TU_Index == TU_Index_Start or TU_Index <= 0: # Hopefully this shouldn't happen
                continue # but at the very least this should prevent corrupting the export
            
            TU_Index_Start = TU_File_Content.index('</technique>', TU_Index_Start, TU_Index_End)
            TU_New_Content = TU_File_Content[:TU_Index] + '\n        <newparam sid="' + img.Image_Surface + '">\n          <surface type="2D">\n            <init_from>' + img.Image_ID + '</init_from>\n          </surface>\n        </newparam>\n        <newparam sid="' + img.Image_Sampler + '">\n          <sampler2D>\n            <source>' + img.Image_Surface + '</source>\n          </sampler2D>\n        </newparam>' + TU_File_Content[TU_Index:TU_Index_Start] + '  <extra>\n            <technique profile="FCOLLADA">\n              <bump>\n                <texture texture="' + img.Image_Sampler + '"/>\n              </bump>\n            </technique>\n          </extra>\n        ' + TU_File_Content[TU_Index_Start:]
            TU_File_Content = TU_New_Content
            write_log(TU_Log_File, " Added new 'technique' element for '" + img.Image_Surface + "'.")
        
        TU_Save_File = open(TU_FilePath, 'wt')
        TU_Save_File.write(TU_New_Content)
        TU_Save_File.close()
        
        if self.debug_log:
            write_log(TU_Log_File, "We're done here. Good night.")
            TU_Log_File.close()
        
        return {'FINISHED'}
 
def TU_Export_Menu(self, context):
    self.layout.operator(
        TU_Export_Collada.bl_idname,
        text="Tower Unite (.dae)",
        icon_value=TU_Icons["tower"].icon_id)