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

from tower_unite_suite.Tower_Icons import TU_Icons as TU_Icons
import tower_unite_suite.TU_Rig_Poses
from tower_unite_suite.TU_Rig_Poses import TU_Poses as TU_Poses
import tower_unite_suite.TU_Rig_Skins
from tower_unite_suite.TU_Rig_Skins import TU_Armature_Skins as TU_Armature_Skins

TU_Bone_Names = ['root', 'pelvis', 'spine_01', 'spine_02', 'spine_03', 'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l', 'index_01_l', 'index_02_l', 'index_03_l', 'middle_01_l', 'middle_02_l', 'middle_03_l', 'pinky_01_l', 'pinky_02_l', 'pinky_03_l', 'ring_01_l', 'ring_02_l', 'ring_03_l', 'thumb_01_l', 'thumb_02_l', 'thumb_03_l', 'lowerarm_twist_01_l', 'upperarm_twist_01_l', 'clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r', 'index_01_r', 'index_02_r', 'index_03_r', 'middle_01_r', 'middle_02_r', 'middle_03_r', 'pinky_01_r', 'pinky_02_r', 'pinky_03_r', 'ring_01_r', 'ring_02_r', 'ring_03_r', 'thumb_01_r', 'thumb_02_r', 'thumb_03_r', 'lowerarm_twist_01_r', 'upperarm_twist_01_r', 'neck_01', 'head', 'thigh_l', 'calf_l', 'calf_twist_01_l', 'foot_l', 'ball_l', 'thigh_twist_01_l', 'thigh_r', 'calf_r', 'calf_twist_01_r', 'foot_r', 'ball_r', 'thigh_twist_01_r']

TU_OriginalBones = {
    'root': {'name': 'root', 'head': (0.0,0.0,0.0), 'tail': (0.0,50.0,0.0), 'roll': 0.0, 'parent': '', 'hide': True},
    'pelvis': {'name': 'pelvis', 'head': (0.008674918673932552,-1.3973468542099,122.48912048339844), 'tail': (0.018128952011466026,-1.3162001371383667,134.73846435546875), 'roll': 1.571649193763733, 'parent': 'root', 'hide': False},
    'spine_01': {'name': 'spine_01', 'head': (0.018169866874814034,-1.31584894657135,134.79148864746094), 'tail': (0.018169842660427094,-1.2843722105026245,146.08480834960938), 'roll': 1.570796251296997, 'parent': 'pelvis', 'hide': False},
    'spine_02': {'name': 'spine_02', 'head': (0.01816987432539463,-1.2843722105026245,146.0848388671875), 'tail': (0.025166818872094154,-0.8167957663536072,156.44354248046875), 'roll': 1.57138192653656, 'parent': 'spine_01', 'hide': False},
    'spine_03': {'name': 'spine_03', 'head': (0.025166818872094154,-0.8167957663536072,156.44354248046875), 'tail': (0.025166528299450874,1.9627726078033447,173.0878143310547), 'roll': 1.570796251296997, 'parent': 'spine_02', 'hide': False},
    'clavicle_l': {'name': 'clavicle_l', 'head': (5.569767475128174,2.383265972137451,169.7222442626953), 'tail': (18.507537841796875,5.539967060089111,168.99908447265625), 'roll': -3.0989644527435303, 'parent': 'spine_03', 'hide': False},
    'upperarm_l': {'name': 'upperarm_l', 'head': (18.507537841796875,5.539967060089111,168.99908447265625), 'tail': (52.76518630981445,7.21614933013916,168.9990692138672), 'roll': -3.1415915489196777, 'parent': 'clavicle_l', 'hide': False},
    'lowerarm_l': {'name': 'lowerarm_l', 'head': (52.76518630981445,7.21614933013916,168.9990692138672), 'tail': (84.41609191894531,5.539971828460693,168.9990692138672), 'roll': 3.141592502593994, 'parent': 'upperarm_l', 'hide': False},
    'hand_l': {'name': 'hand_l', 'head': (84.41609191894531,5.539971828460693,168.9990692138672), 'tail': (93.0940170288086,5.440661907196045,168.5446319580078), 'roll': 1.6411628723144531, 'parent': 'lowerarm_l', 'hide': False},
    'index_01_l': {'name': 'index_01_l', 'head': (93.79058074951172,2.7369580268859863,167.69491577148438), 'tail': (97.46430206298828,2.379713773727417,166.8256378173828), 'roll': 1.9224690198898315, 'parent': 'hand_l', 'hide': False},
    'index_02_l': {'name': 'index_02_l', 'head': (97.46430206298828,2.379713773727417,166.8256378173828), 'tail': (100.28112030029297,2.039702892303467,165.93963623046875), 'roll': 2.003981113433838, 'parent': 'index_01_l', 'hide': False},
    'index_03_l': {'name': 'index_03_l', 'head': (100.28112030029297,2.039702892303467,165.93963623046875), 'tail': (103.1023178100586,2.1720781326293945,165.01319885253906), 'roll': 1.9883404970169067, 'parent': 'index_02_l', 'hide': False},
    'middle_01_l': {'name': 'middle_01_l', 'head': (94.39398193359375,5.065415382385254,167.7309112548828), 'tail': (97.87925720214844,5.167497158050537,167.07504272460938), 'roll': 1.8053569793701172, 'parent': 'hand_l', 'hide': False},
    'middle_02_l': {'name': 'middle_02_l', 'head': (97.87925720214844,5.167497158050537,167.07504272460938), 'tail': (101.0855941772461,5.063799858093262,166.1858673095703), 'roll': 1.8758705854415894, 'parent': 'middle_01_l', 'hide': False},
    'middle_03_l': {'name': 'middle_03_l', 'head': (101.0855941772461,5.063799858093262,166.1858673095703), 'tail': (104.30889129638672,5.058035850524902,165.35386657714844), 'roll': 1.872087836265564, 'parent': 'middle_02_l', 'hide': False},
    'pinky_01_l': {'name': 'pinky_01_l', 'head': (93.01847839355469,8.887332916259766,166.73411560058594), 'tail': (96.57195281982422,9.861875534057617,166.11929321289062), 'roll': 1.6054056882858276, 'parent': 'hand_l', 'hide': False},
    'pinky_02_l': {'name': 'pinky_02_l', 'head': (96.57195281982422,9.861875534057617,166.11929321289062), 'tail': (98.66602325439453,10.398866653442383,165.72891235351562), 'roll': 1.624335765838623, 'parent': 'pinky_01_l', 'hide': False},
    'pinky_03_l': {'name': 'pinky_03_l', 'head': (98.66602325439453,10.398866653442383,165.72891235351562), 'tail': (100.57709503173828,10.837075233459473,164.73805236816406), 'roll': 1.9446704387664795, 'parent': 'pinky_02_l', 'hide': False},
    'ring_01_l': {'name': 'ring_01_l', 'head': (94.0361328125,6.9533491134643555,167.39633178710938), 'tail': (97.23785400390625,7.333095550537109,166.86807250976562), 'roll': 1.6888540983200073, 'parent': 'hand_l', 'hide': False},
    'ring_02_l': {'name': 'ring_02_l', 'head': (97.23785400390625,7.333095550537109,166.86807250976562), 'tail': (100.20158386230469,7.637773513793945,166.23606872558594), 'roll': 1.7352123260498047, 'parent': 'ring_01_l', 'hide': False},
    'ring_03_l': {'name': 'ring_03_l', 'head': (100.20158386230469,7.637773513793945,166.23606872558594), 'tail': (103.11289978027344,7.5847039222717285,165.34304809570312), 'roll': 1.8360638618469238, 'parent': 'ring_02_l', 'hide': False},
    'thumb_01_l': {'name': 'thumb_01_l', 'head': (86.78072357177734,2.392221689224243,167.67904663085938), 'tail': (89.63871002197266,0.015858709812164307,165.5657958984375), 'roll': -2.615170478820801, 'parent': 'hand_l', 'hide': False},
    'thumb_02_l': {'name': 'thumb_02_l', 'head': (89.63871002197266,0.01585543155670166,165.5657958984375), 'tail': (92.41155242919922,-1.3319370746612549,163.89532470703125), 'roll': -2.5540759563446045, 'parent': 'thumb_01_l', 'hide': False},
    'thumb_03_l': {'name': 'thumb_03_l', 'head': (92.41155242919922,-1.3319370746612549,163.89532470703125), 'tail': (95.51835632324219,-1.958494782447815,162.39500427246094), 'roll': -2.4383347034454346, 'parent': 'thumb_02_l', 'hide': False},
    'lowerarm_twist_01_l': {'name': 'lowerarm_twist_01_l', 'head': (84.41609191894531,5.539971828460693,168.9990692138672), 'tail': (116.06700134277344,3.863795757293701,168.9990692138672), 'roll': 3.141592502593994, 'parent': 'lowerarm_l', 'hide': True},
    'upperarm_twist_01_l': {'name': 'upperarm_twist_01_l', 'head': (18.507532119750977,5.539966583251953,168.9990692138672), 'tail': (35.6363639831543,6.378057479858398,168.9990692138672), 'roll': 3.141592502593994, 'parent': 'upperarm_l', 'hide': True},
    'clavicle_r': {'name': 'clavicle_r', 'head': (-5.519443035125732,2.383258104324341,169.72238159179688), 'tail': (-18.457082748413086,5.539926052093506,168.9992218017578), 'roll': 3.098963975906372, 'parent': 'spine_03', 'hide': False},
    'upperarm_r': {'name': 'upperarm_r', 'head': (-18.457073211669922,5.5399394035339355,168.9991455078125), 'tail': (-52.727901458740234,7.4333086013793945,168.9991455078125), 'roll': -3.0864017009735107, 'parent': 'clavicle_r', 'hide': False},
    'lowerarm_r': {'name': 'lowerarm_r', 'head': (-52.727901458740234,7.4333086013793945,168.9991455078125), 'tail': (-84.36587524414062,5.53994607925415,168.9991455078125), 'roll': 3.141592502593994, 'parent': 'upperarm_r', 'hide': False},
    'hand_r': {'name': 'hand_r', 'head': (-84.36587524414062,5.539970397949219,168.999267578125), 'tail': (-95.03248596191406,5.417900562286377,168.44070434570312), 'roll': -1.6411631107330322, 'parent': 'lowerarm_r', 'hide': False},
    'index_01_r': {'name': 'index_01_r', 'head': (-96.08251953125,2.4920599460601807,167.3199920654297), 'tail': (-99.7564926147461,2.1348202228546143,166.45083618164062), 'roll': -1.9224201440811157, 'parent': 'hand_r', 'hide': False},
    'index_02_r': {'name': 'index_02_r', 'head': (-99.7564926147461,2.1348557472229004,166.45079040527344), 'tail': (-102.57332611083984,1.7948424816131592,165.5647735595703), 'roll': -2.0039806365966797, 'parent': 'index_01_r', 'hide': False},
    'index_03_r': {'name': 'index_03_r', 'head': (-102.57335662841797,1.7948744297027588,165.56488037109375), 'tail': (-105.39457702636719,1.9272499084472656,164.63841247558594), 'roll': -1.9883439540863037, 'parent': 'index_02_r', 'hide': False},
    'middle_01_r': {'name': 'middle_01_r', 'head': (-96.67478942871094,4.946051597595215,167.3590850830078), 'tail': (-100.5972900390625,5.0340046882629395,166.58197021484375), 'roll': -1.8146864175796509, 'parent': 'hand_r', 'hide': False},
    'middle_02_r': {'name': 'middle_02_r', 'head': (-100.5972900390625,5.0340046882629395,166.58197021484375), 'tail': (-103.32169342041016,4.931162357330322,165.81707763671875), 'roll': -1.879178524017334, 'parent': 'middle_01_r', 'hide': False},
    'middle_03_r': {'name': 'middle_03_r', 'head': (-103.32169342041016,4.931162357330322,165.81707763671875), 'tail': (-106.06343841552734,4.926253795623779,165.10934448242188), 'roll': -1.8720954656600952, 'parent': 'middle_02_r', 'hide': False},
    'pinky_01_r': {'name': 'pinky_01_r', 'head': (-95.15646362304688,9.487424850463867,166.35548400878906), 'tail': (-98.50334930419922,10.408995628356934,165.77914428710938), 'roll': -1.6048128604888916, 'parent': 'hand_r', 'hide': False},
    'pinky_02_r': {'name': 'pinky_02_r', 'head': (-98.50334930419922,10.408995628356934,165.77914428710938), 'tail': (-100.97069549560547,11.031569480895996,165.19509887695312), 'roll': -1.6608439683914185, 'parent': 'pinky_01_r', 'hide': False},
    'pinky_03_r': {'name': 'pinky_03_r', 'head': (-100.97077178955078,11.031638145446777,165.19546508789062), 'tail': (-103.24201965332031,11.552436828613281,164.0178985595703), 'roll': -1.9446660280227661, 'parent': 'pinky_02_r', 'hide': False},
    'ring_01_r': {'name': 'ring_01_r', 'head': (-96.2842025756836,7.225922584533691,167.01715087890625), 'tail': (-100.12480926513672,7.671341896057129,166.35263061523438), 'roll': -1.6957669258117676, 'parent': 'hand_r', 'hide': False},
    'ring_02_r': {'name': 'ring_02_r', 'head': (-100.12482452392578,7.67136812210083,166.3527069091797), 'tail': (-102.61033630371094,7.984771728515625,165.86740112304688), 'roll': -1.7198671102523804, 'parent': 'ring_01_r', 'hide': False},
    'ring_03_r': {'name': 'ring_03_r', 'head': (-102.6103515625,7.984781265258789,165.86752319335938), 'tail': (-105.04955291748047,7.940317630767822,165.1193084716797), 'roll': -1.8360600471496582, 'parent': 'ring_02_r', 'hide': False},
    'thumb_01_r': {'name': 'thumb_01_r', 'head': (-87.15570068359375,2.0387704372406006,167.36468505859375), 'tail': (-90.01361846923828,-0.3375305235385895,165.25149536132812), 'roll': 2.6151702404022217, 'parent': 'hand_r', 'hide': False},
    'thumb_02_r': {'name': 'thumb_02_r', 'head': (-90.01354217529297,-0.33764514327049255,165.2515106201172), 'tail': (-92.78638458251953,-1.6854385137557983,163.58103942871094), 'roll': 2.5540759563446045, 'parent': 'thumb_01_r', 'hide': False},
    'thumb_03_r': {'name': 'thumb_03_r', 'head': (-92.78639221191406,-1.6854310035705566,163.58103942871094), 'tail': (-95.8931884765625,-2.3119888305664062,162.08071899414062), 'roll': 2.4383327960968018, 'parent': 'thumb_02_r', 'hide': False},
    'lowerarm_twist_01_r': {'name': 'lowerarm_twist_01_r', 'head': (-84.36587524414062,5.53994607925415,168.9991455078125), 'tail': (-116.00383758544922,3.6465868949890137,168.9991455078125), 'roll': 3.141592502593994, 'parent': 'lowerarm_r', 'hide': True},
    'upperarm_twist_01_r': {'name': 'upperarm_twist_01_r', 'head': (-18.457075119018555,5.539942741394043,168.9991912841797), 'tail': (-35.59249496459961,6.486621379852295,168.9991912841797), 'roll': -3.08640193939209, 'parent': 'upperarm_r', 'hide': True},
    'neck_01': {'name': 'neck_01', 'head': (0.023210521787405014,3.0640292167663574,177.22581481933594), 'tail': (0.02358083240687847,1.65865159034729,189.0596923828125), 'roll': 1.570832371711731, 'parent': 'spine_03', 'hide': False},
    'head': {'name': 'head', 'head': (0.02358083240687847,1.65865159034729,189.0596923828125), 'tail': (0.02358078770339489,1.9334630966186523,200.9735565185547), 'roll': 1.570796251296997, 'parent': 'neck_01', 'hide': False},
    'thigh_l': {'name': 'thigh_l', 'head': (8.878706932067871,-0.04258796572685242,114.18891143798828), 'tail': (9.547029495239258,-0.03356553986668587,62.37977600097656), 'roll': -1.927946925163269, 'parent': 'pelvis', 'hide': False},
    'calf_l': {'name': 'calf_l', 'head': (9.547029495239258,-0.03356553614139557,62.37977600097656), 'tail': (9.096607208251953,2.9771361351013184,14.252996444702148), 'roll': -1.9059803485870361, 'parent': 'thigh_l', 'hide': False},
    'calf_twist_01_l': {'name': 'calf_twist_01_l', 'head': (9.140892028808594,2.7552967071533203,17.009429931640625), 'tail': (8.152629852294922,9.786092758178711,-30.68800926208496), 'roll': -1.6044012308120728, 'parent': 'calf_l', 'hide': True},
    'foot_l': {'name': 'foot_l', 'head': (9.07077693939209,3.1497738361358643,11.493339538574219), 'tail': (9.792619705200195,-7.719893932342529,-0.5246662497520447), 'roll': -1.8665215969085693, 'parent': 'calf_l', 'hide': False},
    'ball_l': {'name': 'ball_l', 'head': (9.792619705200195,-7.719893932342529,-0.5246662497520447), 'tail': (8.572949409484863,-23.894323348999023,-0.5834659337997437), 'roll': 1.549655795097351, 'parent': 'foot_l', 'hide': False},
    'thigh_twist_01_l': {'name': 'thigh_twist_01_l', 'head': (9.074851036071777,-0.020381944254040718,113.82501983642578), 'tail': (9.074851036071777,0.07454852759838104,87.71148681640625), 'roll': -1.6235690116882324, 'parent': 'thigh_l', 'hide': True},
    'thigh_r': {'name': 'thigh_r', 'head': (-8.87440299987793,-0.04402130842208862,114.20284271240234), 'tail': (-9.622714042663574,-0.03512828052043915,62.394554138183594), 'roll': 1.9280072450637817, 'parent': 'pelvis', 'hide': False},
    'calf_r': {'name': 'calf_r', 'head': (-9.622714042663574,-0.035128284245729446,62.394554138183594), 'tail': (-9.247116088867188,2.975649118423462,14.2669677734375), 'roll': 1.9063643217086792, 'parent': 'thigh_r', 'hide': False},
    'calf_twist_01_r': {'name': 'calf_twist_01_r', 'head': (-9.287108421325684,2.75380277633667,17.023462295532227), 'tail': (-8.373658180236816,9.784775733947754,-30.67561149597168), 'roll': 1.6051032543182373, 'parent': 'calf_r', 'hide': True},
    'foot_r': {'name': 'foot_r', 'head': (-9.225617408752441,3.148298978805542,11.507277488708496), 'tail': (-9.964261054992676,-7.721506118774414,-0.5095887184143066), 'roll': 1.8788999319076538, 'parent': 'calf_r', 'hide': False},
    'ball_r': {'name': 'ball_r', 'head': (-9.964261054992676,-7.721506118774414,-0.5095887184143066), 'tail': (-8.747121810913086,-23.896135330200195,-0.5665071606636047), 'roll': -1.5525414943695068, 'parent': 'foot_r', 'hide': False},
    'thigh_twist_01_r': {'name': 'thigh_twist_01_r', 'head': (-9.071111679077148,-0.021846788004040718,113.83927154541016), 'tail': (-9.11146354675293,0.07307984679937363,87.72562408447266), 'roll': 1.6242456436157227, 'parent': 'thigh_r', 'hide': True},
}
R90 = 1.5707963267948966 #radians(90)
Spine = ['pelvis', 'spine_01', 'spine_02', 'spine_03', 'neck_01', 'head']
TU_FixedBones = TU_OriginalBones.copy()
for BoneName in TU_FixedBones:
    Bone = TU_FixedBones[BoneName]
    if BoneName in Spine:
        Bone['head'] = (0, Bone['head'][1], Bone['head'][2])
        Bone['tail'] = (0, Bone['tail'][1], Bone['tail'][2])
        Bone['roll'] = R90
        continue
    if Bone['name'][-2:] == '_l':
        OtherBoneName = BoneName[:-2]+'_r'
        OtherBone = TU_FixedBones[OtherBoneName]
        Bone['head'] = (-OtherBone['head'][0], OtherBone['head'][1], OtherBone['head'][2])
        Bone['tail'] = (-OtherBone['tail'][0], OtherBone['tail'][1], OtherBone['tail'][2])
        Bone['roll'] = -OtherBone['roll']

Twist_Bones = {
    'upperarm_twist_01_l': 'upperarm_l',
    'upperarm_twist_01_r': 'upperarm_r',
    'lowerarm_twist_01_l': 'lowerarm_l',
    'lowerarm_twist_01_r': 'lowerarm_r',
    'thigh_twist_01_l': 'thigh_l',
    'thigh_twist_01_r': 'thigh_r',
    'calf_twist_01_l': 'calf_l',
    'calf_twist_01_r': 'calf_r',
    }
    
Finger_Bones_L = ['index_01_l', 'index_02_l', 'index_03_l', 'middle_01_l', 'middle_02_l', 'middle_03_l', 'pinky_01_l', 'pinky_02_l', 'pinky_03_l', 'ring_01_l', 'ring_02_l', 'ring_03_l', 'thumb_01_l', 'thumb_02_l', 'thumb_03_l']
Finger_Bones_R = ['index_01_r', 'index_02_r', 'index_03_r', 'middle_01_r', 'middle_02_r', 'middle_03_r', 'pinky_01_r', 'pinky_02_r', 'pinky_03_r', 'ring_01_r', 'ring_02_r', 'ring_03_r', 'thumb_01_r', 'thumb_02_r', 'thumb_03_r']

pose_skin_options = [('POSE_SKIN_DEFAULT', 'Tower Unite (Default)', '', TU_Icons["tower"].icon_id, 0)] # Add the icon
for Skin in TU_Armature_Skins:
    if Skin == 'Tower Unite (Default)': continue # Already added
    id = len(pose_skin_options)
    identifier = 'POSE_SKIN_'+str(id)
    pose_skin_options.append((identifier, Skin, '', id))

pose_options = [('POSE_DEFAULT', 'Reference Pose (Default)', '', '', 0)]
for Pose in TU_Poses:
    if Pose == 'Reference Pose (Default)': continue # Already added
    id = len(pose_options)
    identifier = 'POSE_'+str(id)
    pose_options.append((identifier, Pose, '', id))