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

import bpy, os
import bpy.utils.previews

# The simplest way to manage previews: this class will do the grunt work for you, allowing you to treat it like a dictionary of previews.
# It will only load previews that are used and will never load the same preview twice, even if used in multiple files.
# Made by Spoom - please credit if you use this in your work.
#
# How to use:
# - import this file into your script
# - Instantiate a Preview_Manager.Preview_Manager object with a dictionary of string-indexed filenames
# - Access previews as dictionary keys, for example: Previews['icon']
# - Remember to call Preview_Manager.clean() when unregistering your module

class Preview_Manager(dict):
    
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
        print(str(self))
    
    def __getitem__(self, key):
        if not key in self.__dict__:
            self.report("ERROR", "SPM: No preview file associated with key '" + str(key) + "' in this instance.")
            return None
        Icons = None
        try:
            Icons = bpy.types.Scene.Spoom_Preview_Manager
        except AttributeError:
            bpy.types.Scene.Spoom_Preview_Manager = bpy.utils.previews.new()
            Icons = bpy.types.Scene.Spoom_Preview_Manager
        
        if not key in Icons:
            self[key] = self.__dict__[key]
        return Icons[key]
        
    def __setitem__(self, key, val):
        bpy.types.Scene.Spoom_Preview_Manager.load(key, os.path.join(os.path.dirname(__file__), "Icons/" + val), 'IMAGE')
    
    def clean(self):
        try:
            bpy.types.Scene.Spoom_Preview_Manager.close()
        except:
            print("Could not delete icons")
        try:
            del bpy.types.Scene.Spoom_Preview_Manager
        except:
            print("Could not close icons")

# Example usage:
#
#from addon import Preview_Manager
#Previews_Name = Preview_Manager.Preview_Manager(
#    foo = 'Foo.png',
#    bar = 'Bar.png',
#)
#Preview = Previews_Name['foo']