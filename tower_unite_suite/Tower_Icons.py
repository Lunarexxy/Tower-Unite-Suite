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

# DISCLAIMER
# The Tower Unite logo's likeness was authorised by PixelTail Games for
# usage as an icon in this Blender Add-on and is not covered by the GPL.

from tower_unite_suite import Preview_Manager
TU_Icons = Preview_Manager.Preview_Manager(
    tower = "TU_Icon.png",
    tower_rig = "Rig.png",
    arms = "Arms_Icon.png",
    arms_raised = "RaisedArms.png",
    arms_lowered = "LoweredArms.png",
    arms_short = "ShortArms.png",
    arms_long = "LongArms.png",
    info = "Info.png",
    shoulders_narrow = "CrissCross.png",
    shoulders_wide = "Vladimir.png",
    shoulders_low = "Tallneck.png",
    walking = "Strut.png",
    running = "Nyoom.png",
    sitting = "Sit.png",
    menacing = "Go.png",
)