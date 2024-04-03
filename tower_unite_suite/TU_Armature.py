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

import bpy
from bpy.types import Menu, Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty, FloatProperty
from mathutils import Matrix, Vector, Euler
from math import radians
import bpy.utils.previews
import importlib

import os
import sys
from bpy_extras.object_utils import object_data_add

from tower_unite_suite.Tower_Icons import TU_Icons as TU_Icons
from tower_unite_suite import TU_Rig_Data as TU_Rig_Data
from tower_unite_suite.TU_Rig_Data import TU_OriginalBones as TU_OriginalBones, TU_FixedBones as TU_FixedBones, TU_Armature_Skins as TU_Armature_Skins, pose_skin_options as pose_skin_options, TU_Bone_Names as TU_Bone_Names, pose_options as pose_options, Twist_Bones as Twist_Bones

from tower_unite_suite import TU_Rig_Poses as TU_Rig_Poses
importlib.reload(TU_Rig_Poses)

from tower_unite_suite.TU_Rig_Poses import TU_Poses as TU_Poses


def CreateBone(context, arm = None, name = "", head = (0,0,0), tail = (0,0,0), roll = 0, parent = '', hide = False):
    bone = arm.edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    bone.roll = roll
    if not parent == '':
        bone.parent = arm.edit_bones[parent]
    # if hide:
        # bone.layers[1] = True
        # bone.layers[0] = False
    return bone

class TU_Armature_PropertyGroup(PropertyGroup):
        
    align_flag_value = 1
    align_flag_Values = [
        ('WORLD', 'World Zero', "Create the armature at (0,0,0)", 'EMPTY_AXIS', 1),
        ('CURSOR', '3D Cursor', "Create the armature at the 3D cursor", 'PIVOT_CURSOR', 2),
        ]  
    
    def align_flag_get(self):
        return TU_Armature_PropertyGroup.align_flag_value
    def align_flag_set(self, value):
        TU_Armature_PropertyGroup.align_flag_value = value
        return None  
    align_flag : EnumProperty(
        items=align_flag_Values,
        name='Place at',
        description='Where to create the armature',
        default={'WORLD'},
        options={'ENUM_FLAG'},
        get=align_flag_get,
        set=align_flag_set)
    
    symmetry_type_value = 1
    symmetry_type_values=[
        ('FIXED', 'Improved', "Use the IMPROVED armature with the right side mirrored", 'SHADERFX', 1),
        ('ORIGINAL', 'Original', "Use the ORIGINAL, asymmetrical armature", 'ARMATURE_DATA', 2),
    ]
    def symmetry_type_get(self):
        return TU_Armature_PropertyGroup.symmetry_type_value
    def symmetry_type_set(self, value):
        TU_Armature_PropertyGroup.symmetry_type_value = value
        return None
    symmetry_type: EnumProperty(
        items=symmetry_type_values,
        name='Symmetry',
        description='Choose which armature to create',
        default={'FIXED'},
        options={'ENUM_FLAG'},
        get=symmetry_type_get,
        set=symmetry_type_set)
    
    pose_skin_value = 0
    def pose_skin_get(self):
        return TU_Armature_PropertyGroup.pose_skin_value
    def pose_skin_set(self, value):
        TU_Armature_PropertyGroup.pose_skin_value = value
        return None
    pose_skin : EnumProperty(
        items=pose_skin_options,
        name='Pose Skin',
        description='Only visible in Pose mode.',
        default='POSE_SKIN_DEFAULT',
        get=pose_skin_get,
        set=pose_skin_set,
        )
    
    twist_bones_value = False
    def twist_bones_get(self):
        return TU_Armature_PropertyGroup.twist_bones_value
    def twist_bones_set(self, value):
        TU_Armature_PropertyGroup.twist_bones_value = value
        return None
    twist_bones: BoolProperty(
        name='Include twist bones (not recommended)',
        description='Twist bones will be hidden on layer 2',
        get=twist_bones_get,
        set=twist_bones_set,
        )

def ArmatureRenameError(self, context):
    self.layout.label(text='Towers Unite requires the Armature be named exactly "Armature" to work,')
    self.layout.label(text='so the existing "Armature" has been renamed.')
    self.layout.label(text='The new Armature is named "Armature".')
    
class Add_TU_Armature(Operator):
    """Add Tower Unite's unique armature"""
    bl_idname = "tower_unite_suite.create_armature"
    bl_label = "Add Tower Unite Armature"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    
    # Necessary properties for object_data_add
    def fake_set(self, value):
        return None
    
    def location_get(self):
        if TU_Armature_PropertyGroup.align_flag_value == 1:
            return (0,0,0)
        else:
            return bpy.context.scene.cursor.location
    location : FloatVectorProperty(
        precision=6,
        options={'HIDDEN', 'SKIP_SAVE'},
        subtype='XYZ',
        get=location_get,
        set=fake_set
        )
    
    def rotation_get(self):
        return (0,0,0)
    rotation : FloatVectorProperty(
        precision=1,
        options={'HIDDEN', 'SKIP_SAVE'},
        subtype='QUATERNION',
        get=rotation_get,
        set=fake_set
        )
    
    def align_get(self):
        return 'WORLD'
    align : StringProperty(
        options={'HIDDEN', 'SKIP_SAVE'},
        get=align_get,
        set=fake_set,
        )
    
    def execute(self, context):
        scene = context.scene
        TU_props = scene.TU_Armature_Props
        
        arm = bpy.data.armatures.new(name='Tower Unite Armature')
        arm_object = object_data_add(context, arm, operator=self, name='Armature')
        if not arm_object.name == 'Armature': # Main Armature object MUST be named 'Armature' - resolve conflicts
            Imposter = bpy.data.objects['Armature'] # sus
            The_Real_Slim_Shady = arm_object.name
            arm_object.name = 'The Real Slim Shady'
            Imposter.name = The_Real_Slim_Shady
            arm_object.name = 'Armature'
            bpy.context.window_manager.popup_menu(ArmatureRenameError, title="Existing 'Armature' object renamed to '" + The_Real_Slim_Shady + "'", icon='ARMATURE_DATA')
        
        arm_object.show_in_front = True
        #arm_object.show_group_colors = True
        
        if 'FIXED' in TU_props.symmetry_type:
            Bones = TU_FixedBones
            arm_object['Rig Type'] = 'FIXED'
        else:
            Bones = TU_OriginalBones
            arm_object['Rig Type'] = 'ORIGINAL'
        
        arm_object['Shoulder Width'] = 0
        arm_object['Shoulder Placement'] = 0
        arm_object['Arms Raised'] = 100
        arm_object['Arm Length'] = 100
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        for BoneName in Bones:
            if not TU_props.twist_bones:
                if '_twist' in BoneName:
                    continue
            Bone = Bones[BoneName]
            NewBone = CreateBone(context, arm = arm, name = Bone['name'], head = Bone['head'], tail = Bone['tail'], roll = Bone['roll'], parent = Bone['parent'], hide = Bone['hide'])
        
        # Colour scheme
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.tower_unite_suite.armature_skin(pose_skin=TU_props.pose_skin)
        bpy.ops.object.mode_set(mode='EDIT')
        return bpy.ops.tower_unite_suite.edit_armature('INVOKE_DEFAULT')
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)       
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        Props = scene.TU_Armature_Props
        row = layout.row()
        row.label(text='Location', icon='VIEW3D')
        row.prop(Props, 'align_flag', expand=True)
        split = row.split()
        row = layout.row()
        row.label(text='Armature', icon_value=TU_Icons['tower_rig'].icon_id)
        row.prop(Props, 'symmetry_type', expand=True)
        split = row.split()
        row = layout.row()
        row.label(icon='BRUSHES_ALL')
        row.prop(Props, 'pose_skin')
        split = row.split()
        row = layout.row()
        row.label(icon='CONSTRAINT_BONE')
        row.prop(Props, 'twist_bones')
        split = row.split()

def TU_Spawn_Armature_Button(self, context):
    self.layout.operator(
        Add_TU_Armature.bl_idname,
        text="Tower Unite Armature",
        icon_value=TU_Icons["tower"].icon_id)

def Verify_TU_Armature(arm):
    if not arm.type == 'ARMATURE': return False
    if len(arm.data.bones) > 61: return False
    for bone in arm.data.bones:
        if not bone.name in TU_Bone_Names: return False
    return True

# Edit menu
class TU_Armature_Edit_Menu(Menu):
    bl_idname = "VIEW3D_MT_edit_tower"
    bl_label = "Tower Unite Rig"

    def draw(self, context):
        layout = self.layout
        layout.operator(Adjust_TU_Armature.bl_idname, text="Adjust", icon="ORIENTATION_LOCAL")

def TU_Armature_Edit_Menu_Item(self, context):
    self.layout.separator()
    if Verify_TU_Armature(context.edit_object):
        self.layout.menu(TU_Armature_Edit_Menu.bl_idname, icon_value=TU_Icons["tower"].icon_id)
    else:
        self.layout.label(text=TU_Armature_Edit_Menu.bl_label + ' (invalid)', icon_value=TU_Icons["tower"].icon_id)

class TU_Adjust_Armature_PropertyGroup(PropertyGroup):
    @staticmethod
    def arm_upd(context, BoneList, Origin, Degrees, Length, BoneData, Offset):
        arm = context.edit_object
        x, y, z = arm.original.matrix_world.to_3x3().col
        R = (Matrix.Rotation(Degrees, 4, y))
        for BoneName in BoneList:
            if not BoneName in arm.data.edit_bones:
                continue
            bone = arm.data.edit_bones[BoneName]
            Head = Vector(BoneData[BoneName]['head'])
            Tail = Vector(BoneData[BoneName]['tail'])
            Vec = (Head - Origin) * Length
            Vec.rotate(R)
            Vec = Vec + Origin + Offset
            bone.head = Vec[:]
            Vec = (Tail - Origin) * Length
            Vec.rotate(R)
            Vec = Vec + Origin + Offset
            bone.tail = Vec[:]
            bone.roll = BoneData[BoneName]['roll'] + Degrees

    def arms_upd(self, context):
        arm = context.edit_object
        Bones = arm.data.edit_bones
        Props = context.scene.TU_Adjust_Armature_Props
        left_forearm = ['lowerarm_l', 'hand_l', 'index_01_l', 'index_02_l', 'index_03_l', 'middle_01_l', 'middle_02_l', 'middle_03_l', 'pinky_01_l', 'pinky_02_l', 'pinky_03_l', 'ring_01_l', 'ring_02_l', 'ring_03_l', 'thumb_01_l', 'thumb_02_l', 'thumb_03_l', 'lowerarm_twist_01_l', 'upperarm_twist_01_l']
        right_forearm = ['lowerarm_r', 'hand_r', 'index_01_r', 'index_02_r', 'index_03_r', 'middle_01_r', 'middle_02_r', 'middle_03_r', 'pinky_01_r', 'pinky_02_r', 'pinky_03_r', 'ring_01_r', 'ring_02_r', 'ring_03_r', 'thumb_01_r', 'thumb_02_r', 'thumb_03_r', 'lowerarm_twist_01_r', 'upperarm_twist_01_r']
        Original = arm.original
        BoneData = TU_FixedBones
        if "Rig Type" in Original:
            if Original["Rig Type"] == "ORIGINAL":
                BoneData = TU_OriginalBones
        
        ArmsRaisedDegrees = radians((100 - Props.t_pose) * 0.9)
        ArmsLengthModifier= Props.arm_length * 0.01
        
        LeftOffset = Vector((Props.shoulder_width,0,-Props.shoulder_height))
        RightOffset = Vector((-Props.shoulder_width,0,-Props.shoulder_height))
        
        #Shoulders
        LeftOrigin = Vector(BoneData['clavicle_l']['head'])
        RightOrigin = Vector(BoneData['clavicle_r']['head'])
        self.arm_upd(context, ['clavicle_l'], LeftOrigin, 0, 1, BoneData, LeftOffset)
        self.arm_upd(context, ['clavicle_r'], RightOrigin, 0, 1, BoneData, RightOffset)
        
        #Biceps
        LeftOrigin = Vector(BoneData['upperarm_l']['head'])
        RightOrigin = Vector(BoneData['upperarm_r']['head'])
        self.arm_upd(context, ['upperarm_l'], LeftOrigin, ArmsRaisedDegrees, ArmsLengthModifier, BoneData, LeftOffset)
        self.arm_upd(context, ['upperarm_r'], RightOrigin, -ArmsRaisedDegrees, ArmsLengthModifier, BoneData, RightOffset)
        
        #Elbows and below
        self.arm_upd(context, left_forearm, LeftOrigin, ArmsRaisedDegrees, ArmsLengthModifier, BoneData, LeftOffset)
        self.arm_upd(context, right_forearm, RightOrigin, -ArmsRaisedDegrees, ArmsLengthModifier, BoneData, RightOffset)
        
        Original['Shoulder Width'] = Props.shoulder_width
        Original['Shoulder Placement'] = Props.shoulder_height
        Original['Arms Raised'] = Props.t_pose
        Original['Arm Length'] = Props.arm_length
        
#    t_pose_value = R90 # Angle values work fine but do not have the desired slider effect
    t_pose_value = 100
    def t_pose_get(self):
        return TU_Adjust_Armature_PropertyGroup.t_pose_value
    def t_pose_set(self, value):
        TU_Adjust_Armature_PropertyGroup.t_pose_value = value
    
    t_pose : FloatProperty(
        name="Raised arms",
        description="100% will be a perfect 'T pose' with arms raised. Lower values relax the arms towards an 'A pose'. Use this to align the armature with your mesh",
        default=100,
        min=0.0,
        max=100,
        soft_min=0.0,
        soft_max=100,
        precision=0,
        step=1,
        #subtype='ANGLE',
        subtype='PERCENTAGE',
        get=t_pose_get,
        set=t_pose_set,
        update=arms_upd,
        )
    
    arm_len = 100
    def arm_len_get(self):
        return TU_Adjust_Armature_PropertyGroup.arm_len
    def arm_len_set(self, value):
        TU_Adjust_Armature_PropertyGroup.arm_len = value
    arm_length : FloatProperty(
        name="Arm length*",
        description="This does not change the length of the arms once imported into Tower Unite. Use this only to align the rig with your model",
        default=100,
        min=50.0,
        max=150.0,
        soft_min=50.0,
        soft_max=150.0,
        precision=0,
        step=10,
        subtype='PERCENTAGE',
        get=arm_len_get,
        set=arm_len_set,
        update=arms_upd,
        )
    
    shoulder_width_value = 0
    def shoulder_width_get(self):
        return TU_Adjust_Armature_PropertyGroup.shoulder_width_value
    def shoulder_width_set(self, value):
        TU_Adjust_Armature_PropertyGroup.shoulder_width_value = value
    shoulder_width : FloatProperty(
        name="Shoulder Width",
        description="Shoulder values will reset when importing to Tower Unite. Match the values here to your metadata there",
        default=0,
        min=-50.0,
        max=50.0,
        soft_min=-50.0,
        soft_max=50.0,
        precision=0,
        step=100,
        subtype='NONE',
        get=shoulder_width_get,
        set=shoulder_width_set,
        update=arms_upd,
        )
    
    shoulder_height_value = 0
    def shoulder_height_get(self):
        return TU_Adjust_Armature_PropertyGroup.shoulder_height_value
    def shoulder_height_set(self, value):
        TU_Adjust_Armature_PropertyGroup.shoulder_height_value = value
    shoulder_height : FloatProperty(
        name="Shoulder Position",
        description="Shoulder values will reset when importing to Tower Unite. Match the values here to your metadata there",
        default=0,
        min=0.0,
        max=20.0,
        soft_min=0.0,
        soft_max=20.0,
        precision=0,
        step=100,
        subtype='UNSIGNED',
        get=shoulder_height_get,
        set=shoulder_height_set,
        update=arms_upd,
        )
    
    def PopulateCustomProperties(length, height, width, angle):
        TU_Adjust_Armature_PropertyGroup.shoulder_height_value = 0
        TU_Adjust_Armature_PropertyGroup.shoulder_width_value = 0
        TU_Adjust_Armature_PropertyGroup.arm_len = value
        TU_Adjust_Armature_PropertyGroup.t_pose_value = value

class Adjust_TU_Armature(Operator):
    """Adjust the Tower Unite armature"""
    bl_idname = "tower_unite_suite.edit_armature"
    bl_label = "Adjust Tower Unite Rig"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    
    def execute(self, context):
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        Props = context.scene.TU_Adjust_Armature_Props
        Arm = context.edit_object
        
        # To prevent errors, set defaults for Armatures created pre-1.1.0
        if not 'Shoulder Width' in Arm: Arm['Shoulder Width'] = 0
        if not 'Shoulder Placement' in Arm: Arm['Shoulder Placement'] = 0
        if not 'Arms Raised' in Arm: Arm['Arms Raised'] = 100
        if not 'Arm Length' in Arm: Arm['Arm Length'] = 100
        
        # Inject the Custom Properties into the PropertyGroup to keep values set previously after adjusting another armature.
        TU_Adjust_Armature_PropertyGroup.shoulder_height_value = max(0, min(20, Arm['Shoulder Placement']))
        TU_Adjust_Armature_PropertyGroup.shoulder_width_value = max(-50, min(50, Arm['Shoulder Width']))
        TU_Adjust_Armature_PropertyGroup.arm_len = max(50, min(150, Arm['Arm Length']))
        TU_Adjust_Armature_PropertyGroup.t_pose_value = max(0, min(100, Arm['Arms Raised']))
        
        context.window_manager.invoke_props_dialog(self)   
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        Props = scene.TU_Adjust_Armature_Props
        row = layout.row()
        row.label(text = 'SHOULDERS', icon='CON_ARMATURE')
        split = row.split()
        row = layout.row()
        row.label(icon_value=TU_Icons['shoulders_narrow'].icon_id)
        row.prop(Props, 'shoulder_width')
        row.label(icon_value=TU_Icons['shoulders_wide'].icon_id)
        split = row.split()
        row = layout.row()
        row.label(icon_value=TU_Icons['tower_rig'].icon_id)
        row.prop(Props, 'shoulder_height')
        row.label(icon_value=TU_Icons['shoulders_low'].icon_id)
        split = row.split()
        row = layout.row()
        row.label(text='Replicate these values in Tower Unite\'s Metadata.', icon='SORTBYEXT')
        split = row.split()
        row = layout.row()
        row.separator(factor=2.0)
        split = row.split()
        row = layout.row()
        row.label(text = 'ARMS', icon_value=TU_Icons['arms'].icon_id)
        split = row.split()
        row = layout.row()
        row.label(icon_value=TU_Icons['arms_lowered'].icon_id)
        row.prop(Props, 't_pose')
        row.label(icon_value=TU_Icons['arms_raised'].icon_id)
        split = row.split()
        row = layout.row()
        row.label(icon_value=TU_Icons['arms_short'].icon_id)
        row.prop(Props, 'arm_length')
        row.label(icon_value=TU_Icons['arms_long'].icon_id)
        split = row.split()
        row = layout.row()
        row.label(text='Arm length will be reset to 100% in Tower Unite.', icon='SORTBYEXT')
        split = row.split()
        row = layout.row()
        row.separator(factor=2.0)
        split = row.split()
        row = layout.row()
        row.label(text='Use these sliders only to align the rig to your model.', icon_value=TU_Icons['info'].icon_id)
        split = row.split()

#Pose Menu
       

class TU_Armature_Pose_Menu(Menu):
    bl_idname = "VIEW3D_MT_pose_tower"
    bl_label = "Tower Unite Rig"
    def draw(self, context):
        layout = self.layout
        layout.menu(TU_Armature_Poses_Menu.bl_idname, icon="ARMATURE_DATA")
        layout.separator()
        layout.operator(TU_Armature_Skin.bl_idname, text="Change Skin", icon="BRUSHES_ALL")
 
class TU_Armature_Poses_Menu(Menu):
    bl_idname = "VIEW3D_MT_poses_tower"
    bl_label = "Preview Pose"
    def draw(self, context):
        layout = self.layout
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Reference Pose", icon_value=TU_Icons['arms_raised'].icon_id)
        pose_item.preselectedpose = 'Reference Pose (Default)'
        layout.separator()
        layout.menu(TU_Armature_Poses_Standing_Menu.bl_idname, icon_value=TU_Icons['arms_lowered'].icon_id)
        layout.menu(TU_Armature_Poses_Walking_Menu.bl_idname, icon_value=TU_Icons['walking'].icon_id)
        layout.menu(TU_Armature_Poses_Running_Menu.bl_idname, icon_value=TU_Icons['running'].icon_id)
        layout.menu(TU_Armature_Poses_Sitting_Menu.bl_idname, icon_value=TU_Icons['sitting'].icon_id)
        layout.menu(TU_Armature_Poses_Other_Menu.bl_idname, icon='QUESTION')
        layout.separator()
        layout.label(text='Marked poses provided by PixelTail Games.', icon_value=TU_Icons['tower'].icon_id)

class TU_Armature_Poses_Standing_Menu(Menu):
    bl_idname = "VIEW3D_MT_poses_standing_tower"
    bl_label = "Standing"
    def draw(self, context):
        layout = self.layout
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Idle", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Idle*'
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Relaxed", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Relaxed*'
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Fight!", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Fight!*'
        layout.separator()
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Menacing", icon_value=TU_Icons['menacing'].icon_id)
        pose_item.preselectedpose = 'Menacing'
        
class TU_Armature_Poses_Walking_Menu(Menu):
    bl_idname = "VIEW3D_MT_poses_walking_tower"
    bl_label = "Walking"
    def draw(self, context):
        layout = self.layout
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Left foot forward", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Walk (Left)*'
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Right foot forward", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Walk (Right)*'
        layout.separator()
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Yakuza")
        pose_item.preselectedpose = 'Walk (Yakuza)'
        
class TU_Armature_Poses_Running_Menu(Menu):
    bl_idname = "VIEW3D_MT_poses_running_tower"
    bl_label = "Running"
    def draw(self, context):
        layout = self.layout
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Left foot forward", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Run (Left)*'
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Right foot forward", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Run (Right)*'
        layout.separator()
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Ninja")
        pose_item.preselectedpose = 'Run (Ninja)'
        
class TU_Armature_Poses_Sitting_Menu(Menu):
    bl_idname = "VIEW3D_MT_poses_sitting_tower"
    bl_label = "Sitting"
    def draw(self, context):
        layout = self.layout
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Emote", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Sitting (Emote)*'
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Chair", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Sitting (Chair)*'
        
class TU_Armature_Poses_Other_Menu(Menu):
    bl_idname = "VIEW3D_MT_poses_other_tower"
    bl_label = "Other"
    def draw(self, context):
        layout = self.layout
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Laid Back", icon_value=TU_Icons['tower'].icon_id)
        pose_item.preselectedpose = 'Laid Back*'
        pose_item = layout.operator(TU_Armature_Pose.bl_idname, text="Ragdoll")
        pose_item.preselectedpose = 'Ragdoll'

Rays = ['upperarm_l', 'lowerarm_l', 'upperarm_r', 'lowerarm_r', 'thigh_l', 'calf_l', 'thigh_r', 'calf_r', 'neck_01']

class TU_Armature_Skin(Operator):
    """Set the Tower Unite armature's skin in Pose Mode"""
    bl_idname = "tower_unite_suite.armature_skin"
    bl_label = "Tower Unite Rig Pose-Mode Skin"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    
    pose_skin_value = 0
    def pose_skin_get(self):
        return TU_Armature_PropertyGroup.pose_skin_value
    def pose_skin_set(self, value):
        TU_Armature_PropertyGroup.pose_skin_value = value
        return None
    def pose_skin_upd(self, context):
        Pose = context.pose_object.pose
        for SkinID in range(0,len(pose_skin_options)):
            Skin = pose_skin_options[SkinID]
            if not Skin[0] == self.pose_skin: continue
            if Skin[1] == 'Ray': S = 1
            else: S = 0
            H = 1 - S
            for R in Rays:
                B = context.pose_object.data.bones[R]
                B.layers[S] = True
                B.layers[H] = False
            Scheme = TU_Armature_Skins[Skin[1]]
            if not 'Hidden' in Pose.bone_groups:
                bpy.ops.pose.group_add()
                HiddenBoneGroup = Pose.bone_groups[len(Pose.bone_groups)-1]
                HiddenBoneGroup.name = 'Hidden'
                HiddenBoneGroup.color_set = 'CUSTOM'
            else:
                HiddenBoneGroup = Pose.bone_groups['Hidden']
            HiddenBoneGroup.colors.normal = Scheme['Hidden']
            HiddenBoneGroup.colors.select = Scheme['Select']
            HiddenBoneGroup.colors.active = Scheme['Active']
            for BoneName in TU_Bone_Names:
                if not BoneName in Pose.bones: continue
                PoseBone = Pose.bones[BoneName]
                if TU_FixedBones[BoneName]['hide']:
                    PoseBone.bone_group = HiddenBoneGroup
                    continue
                BoneObj = PoseBone.bone
                if not BoneName in Pose.bone_groups:
                    BoneObj.select = True
                    bpy.ops.pose.group_assign(type=0)
                    BoneObj.select = False
                    BoneGroup = Pose.bone_groups[len(Pose.bone_groups)-1]
                    BoneGroup.name = BoneName
                    BoneGroup.color_set = 'CUSTOM'
                else:
                    BoneGroup = Pose.bone_groups[BoneName]
                BoneGroup.colors.normal = Scheme[BoneName]
                BoneGroup.colors.select = Scheme['Select']
                BoneGroup.colors.active = Scheme['Active']
            break
            
    
    pose_skin : EnumProperty(
        items=pose_skin_options,
        name='Pose Skin',
        description='Only visible in Pose mode.',
        default='POSE_SKIN_DEFAULT',
        get=pose_skin_get,
        set=pose_skin_set,
        update=pose_skin_upd,
        )
    
    def execute(self, context):
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)       
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.ui_units_x = 17
        scene = context.scene
        row = layout.row()
        row.label(text = 'Choose a skin:', icon='BRUSHES_ALL')
        row.prop(self, 'pose_skin', text='')
        split = row.split()

class TU_Pose_Armature_PropertyGroup(PropertyGroup):
    pose_value = 0
    def pose_get(self):
        return TU_Pose_Armature_PropertyGroup.pose_value
    def pose_set(self, value):
        TU_Pose_Armature_PropertyGroup.pose_value = value
        return None
    def pose_upd(self, context):
        Key = None
        CheckPose = self.pose
        for PoseData in pose_options:
            if not PoseData[0] == CheckPose: continue
            Key = PoseData[1]
        if not Key: return None
        P_dat = TU_Poses[Key]
        P_obj = context.pose_object.pose
        context.pose_object.data.pose_position = 'POSE'
        for Bone in P_dat:
            if not Bone in P_obj.bones: continue
            B_obj = P_obj.bones[Bone]
            B_obj.matrix_basis = P_dat[Bone]
            if 'Arms Raised' in context.pose_object:
                if Bone == 'upperarm_l' or Bone == 'upperarm_r':
                    B_obj.rotation_quaternion.rotate(Euler((-radians((100-context.pose_object['Arms Raised'])*0.9),0,0), 'XYZ'))
    
    pose : EnumProperty(
        items=pose_options,
        name='Pose',
        description='Preview your model with a pose.',
        default='POSE_DEFAULT',
        get=pose_get,
        set=pose_set,
        update=pose_upd,
        )

class TU_Armature_Pose(Operator):
    """Set the Tower Unite armature's pose"""
    bl_idname = "tower_unite_suite.armature_pose"
    bl_label = "Tower Unite pose preview"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    
    preselectedpose : StringProperty(
        default='NONE',
        options={'HIDDEN', 'SKIP_SAVE'}
        )
    
    def execute(self, context):
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if not self.preselectedpose == 'NONE':
            for k in pose_options:
                if self.preselectedpose == k[1]:
                    context.scene.TU_Pose_Armature_Props.pose = k[0]
            
        context.window_manager.invoke_props_dialog(self)       
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.ui_units_x = 17
        scene = context.scene
        Props = scene.TU_Pose_Armature_Props
        row = layout.row()
        row.label(text = 'Choose a pose:', icon='ARMATURE_DATA')
        row.prop(Props, 'pose', text='')
        split = row.split()
        row = layout.row()
        row.label(text='Marked poses provided by PixelTail Games.', icon='SORTBYEXT')
        split = row.split()

def TU_Armature_Pose_Menu_Item(self, context):
    self.layout.separator()
    if Verify_TU_Armature(context.pose_object):
        self.layout.menu(TU_Armature_Pose_Menu.bl_idname, icon_value=TU_Icons["tower"].icon_id)
    else:
        self.layout.label(text=TU_Armature_Pose_Menu.bl_label + ' (invalid)', icon_value=TU_Icons["tower"].icon_id)
