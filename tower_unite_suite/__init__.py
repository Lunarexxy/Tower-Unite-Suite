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

bl_info = {
    "name": "Tower Unite Suite (Blender 4.0 beta ver.)",
    "author": "Spoom Wolf (Spoom#0001)",
    "version": (1, 3, 74),
    "blender": (3, 2, 1),
    "location": "File > Export > Tower Unite & various menus",
    "description": "Varied tool suite for Tower Unite workshop models.",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

import bpy
import bpy.utils.previews
import importlib
from tower_unite_suite import Tower_Icons
importlib.reload(Tower_Icons)
from tower_unite_suite import TU_Armature
importlib.reload(TU_Armature)
from tower_unite_suite import TU_Export
importlib.reload(TU_Export)
#from tower_unite_suite import TU_Material
#importlib.reload(TU_Material) # RIP United_BSDF. We hardly knew you.

from tower_unite_suite.Tower_Icons import TU_Icons as TU_Icons
from tower_unite_suite.TU_Armature import (Add_TU_Armature, TU_Armature_PropertyGroup, TU_Spawn_Armature_Button, TU_Armature_Edit_Menu, TU_Armature_Edit_Menu_Item, Adjust_TU_Armature, TU_Adjust_Armature_PropertyGroup, TU_Armature_Skin, TU_Armature_Pose, TU_Pose_Armature_PropertyGroup,
    TU_Armature_Pose_Menu_Item, TU_Armature_Pose_Menu, TU_Armature_Poses_Menu, TU_Armature_Poses_Standing_Menu, TU_Armature_Poses_Walking_Menu, TU_Armature_Poses_Running_Menu, TU_Armature_Poses_Sitting_Menu, TU_Armature_Poses_Other_Menu)
from tower_unite_suite.TU_Export import TU_Export_Collada, TU_Export_Menu
#from tower_unite_suite.TU_Material import Unite_Material, Unite_Material_Panel

Registered_Classes = [
    # TU_Export.py
    TU_Export_Collada,
    # TU_Armature.py
    Add_TU_Armature, TU_Armature_PropertyGroup, TU_Armature_Edit_Menu, Adjust_TU_Armature, TU_Adjust_Armature_PropertyGroup, TU_Armature_Skin, TU_Armature_Pose,
    TU_Pose_Armature_PropertyGroup, TU_Armature_Pose_Menu, TU_Armature_Poses_Menu, TU_Armature_Poses_Standing_Menu, TU_Armature_Poses_Walking_Menu, TU_Armature_Poses_Running_Menu, TU_Armature_Poses_Sitting_Menu, TU_Armature_Poses_Other_Menu,
    # TU_Material.py
    #Unite_Material, Unite_Material_Panel,
    ]

def register():
    TU_Export.addon_version = str(bl_info['version'])
    
    from bpy.utils import register_class
    for cl in Registered_Classes:
        register_class(cl)
    
    # Export
    bpy.types.TOPBAR_MT_file_export.append(TU_Export_Menu)
    
    # Armature
    bpy.types.VIEW3D_MT_armature_add.append(TU_Spawn_Armature_Button)
    bpy.types.VIEW3D_MT_edit_armature.append(TU_Armature_Edit_Menu_Item)
    bpy.types.VIEW3D_MT_pose.append(TU_Armature_Pose_Menu_Item)
    bpy.types.Scene.TU_Armature_Props = bpy.props.PointerProperty(type = TU_Armature_PropertyGroup)
    bpy.types.Scene.TU_Adjust_Armature_Props = bpy.props.PointerProperty(type = TU_Adjust_Armature_PropertyGroup)
    bpy.types.Scene.TU_Pose_Armature_Props = bpy.props.PointerProperty(type = TU_Pose_Armature_PropertyGroup)

def unregister():
    TU_Icons.clean()
    
    from bpy.utils import unregister_class
    for cl in Registered_Classes:
        try:
            unregister_class(cl)
        except:
            print("Error unregistering TU-Suite class " + str(cl))
    
    # Export
    bpy.types.TOPBAR_MT_file_export.remove(TU_Export_Menu)
    
    # Armature
    bpy.types.VIEW3D_MT_armature_add.remove(TU_Spawn_Armature_Button)
    bpy.types.VIEW3D_MT_edit_armature.remove(TU_Armature_Edit_Menu_Item)
    bpy.types.VIEW3D_MT_pose.remove(TU_Armature_Pose_Menu_Item)
    del bpy.types.Scene.TU_Armature_Props
    del bpy.types.Scene.TU_Adjust_Armature_Props
    del bpy.types.Scene.TU_Pose_Armature_Props
    
    from tower_unite_suite.TU_Material import Unregister
    TU_Material.Unregister()
    
if __name__ == "__main__":
    register()