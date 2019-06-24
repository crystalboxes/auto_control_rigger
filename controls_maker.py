import hou, utl, character_utils
from character import Character

class IKData:
    def __init__(self, character, start_bone, end_bone):
        self.character = character 
        self.start_bone = start_bone

        # Left arm
        self.end_bone = self.character.LeftForeArm
        self.KIN_name = "KIN_arm_left"
        self.IK_affector_ptr_name = "IK_wrist_left_ptr"
        self.IK_affector_name = "ctrl_IK_wrist_left"
        self.IK_twist_ptr_name = "IK_arm_twist_left_ptr"
        self.IK_twist_name = "ctrl_IK_arm_twist_left"
        self.blend_node_name = "rig_IK_wrist_left_orientation"
        self.IK_twist_offset_parm_name = "tx"
        self.IK_twist_offset = .2
        self.IK_twist_degrees = -90.0

        if start_bone == self.character.RightArm:
            self.end_bone = self.character.RightForeArm
            self.KIN_name = "KIN_arm_right"
            self.IK_affector_ptr_name = "IK_wrist_right_ptr"
            self.IK_affector_name = "ctrl_IK_wrist_right"
            self.IK_twist_ptr_name = "IK_arm_twist_right_ptr"
            self.IK_twist_name = "ctrl_IK_arm_twist_right"
            self.blend_node_name = "rig_IK_wrist_right_orientation"
            self.IK_twist_offset *= -1
            self.IK_twist_degrees *= -1
        elif start_bone == self.character.LeftUpLeg:
            self.end_bone = self.character.LeftLeg
            self.KIN_name = "KIN_leg_left"
            self.IK_affector_ptr_name = "rig_foot_ankle_left_ptr"
            self.IK_affector_name = "rig_foot_ankle_left"
            self.IK_twist_ptr_name = "IK_leg_twist_left_ptr"
            self.IK_twist_name = "ctrl_IK_leg_twist_left"
            self.blend_node_name = "rig_IK_ankle_left_orientation"
            self.IK_twist_offset_parm_name = "ty"
            self.IK_twist_offset = .45
            self.IK_twist_degrees *= 0
        elif start_bone == self.character.RightUpLeg:
            self.end_bone = self.character.RightLeg
            self.KIN_name = "KIN_leg_right"
            self.IK_affector_ptr_name = "rig_foot_ankle_right_ptr"
            self.IK_affector_name = "rig_foot_ankle_right"
            self.IK_twist_ptr_name = "IK_leg_twist_right_ptr"
            self.IK_twist_name = "ctrl_IK_leg_twist_right"
            self.blend_node_name = "rig_IK_ankle_right_orientation"
            self.IK_twist_offset_parm_name = "ty"
            self.IK_twist_offset = .45
            self.IK_twist_degrees *= 0
        
        if end_bone:
            self.end_bone = end_bone

class CharacterManager:
    def __init__(self, fbx):
        self.fbx = fbx
        self.chopnet = get_chopnet_in_character_subnet(fbx)
        self.character = Character(fbx)
        self.controls_nodes = []

        self.master_input = fbx.indirectInputs()[0]
        self.ik_controls_space_node = None
        self.ik_node_pos_x = 0

    def setup_controls(self):
        if not self.master_input.outputConnections():
            self.setup_character_transforms()
            self.add_ik(self.character.RightArm)
            self.add_ik(self.character.LeftArm)

            self.add_ik(self.character.RightUpLeg)
            self.add_ik(self.character.LeftUpLeg)

            if self.bone_has_valid_joint(self.character.LeftHandIndex1):
                self.add_fingers_controls()

            if self.bone_has_valid_joint(self.character.Spine1, output=True) and \
               self.bone_has_valid_joint(self.character.Spine1) and \
               self.bone_has_valid_joint(self.character.Spine):
                self.add_spine_controls()
            
            if self.bone_has_valid_joint(self.character.Neck) and \
               self.bone_has_valid_joint(self.character.Head):
                self.add_head_controls()

        for control_node in self.controls_nodes:
            control_node.setDisplayFlag(True)
            control_node.setSelectableInViewport(True)
            control_node.setColor(self.ctrl_node_color())

    def bone_has_valid_joint(self, bone, output=False):
        if bone:
            if output:
                connections = bone.outputConnections()
                if connections:
                    return connections[0].outputNode().type().name() == "null"
            else:    
                connections = bone.inputConnections()
                if connections:
                    return connections[0].inputNode().type().name() == "null"
        return False
    
    def add_head_controls(self):
        neck = self.character.Neck.inputConnections()[0].inputNode()
        head = self.character.Head.inputConnections()[0].inputNode()
        neck.setParms({ 
            "geoscale" : .2, 
            "geosizex" : .4, "geosizey" : 2, "geosizez" : 1,
            "geocenterx" : 0, "geocentery" : -.1, "geocenterz" : 0,
            "controltype" : 3, 
            "orientation" : 3, 
            "shadedmode" : False 
        })
        head.setParms({ 
            "geoscale" : .3, 
            "controltype" : 2, 
            "shadedmode" : False 
        })
        self.controls_nodes.append(neck)
        self.controls_nodes.append(head)
        utl.lock_parms(neck, ["scale"], ["t", "s", "p"])
        utl.lock_parms(head, ["scale"], ["t", "s", "p"])


    def add_spine_controls(self):
        spine_joints = [
            self.character.Spine1.outputConnections()[0].outputNode(),
            self.character.Spine1.inputConnections()[0].inputNode(),
            self.character.Spine.inputConnections()[0].inputNode()
        ]

        default_scale = .55
        scale_increment = .05

        for x, spine in enumerate(spine_joints):
            orientation = 3
            if x == 0:
                orientation = 2 # ZX orientation for 
            spine.setParms({ "geoscale" : default_scale + scale_increment * x, "controltype" : 1, "orientation" : orientation, "shadedmode" : False })
            utl.lock_parms(spine, ["scale"], ["t", "s", "p"])
            self.controls_nodes.append(spine)

    def add_fingers_controls(self):
        finger_nodes = [self.character.LeftHandIndex1, self.character.LeftHandIndex2, self.character.LeftHandIndex3,
        self.character.LeftHandMiddle1, self.character.LeftHandMiddle2, self.character.LeftHandMiddle3,
        self.character.LeftHandRing1, self.character.LeftHandRing2, self.character.LeftHandRing3,
        self.character.LeftHandPinky1, self.character.LeftHandPinky2, self.character.LeftHandPinky3,
        self.character.LeftHandThumb1, self.character.LeftHandThumb2, self.character.LeftHandThumb3,

        self.character.RightHandIndex1, self.character.RightHandIndex2, self.character.RightHandIndex3,
        self.character.RightHandMiddle1, self.character.RightHandMiddle2, self.character.RightHandMiddle3,
        self.character.RightHandRing1, self.character.RightHandRing2, self.character.RightHandRing3,
        self.character.RightHandPinky1, self.character.RightHandPinky2, self.character.RightHandPinky3,
        self.character.RightHandThumb1, self.character.RightHandThumb2, self.character.RightHandThumb3,]

        for idx, finger_node in enumerate(finger_nodes):
            base_scale = 6
            scale_unit = 0.01
            scale = base_scale * scale_unit - scale_unit * (idx % 3)
            null = finger_node.inputConnections()[0].inputNode()
            null.setParms({
                "geoscale" : scale, "geosizex" : .4, "geosizey" : 1, "geosizez" : .5,
                "geocenterx" : 0, "geocentery" : -.006, "geocenterz" : 0,
                "displayicon" : 0, "controltype": 1, "orientation" : 3, "shadedmode" : False
            })
            utl.lock_parms(null, ["scale"], ["t", "s", "p"])
            self.controls_nodes.append(null)


    def ik_node_pos(self):
        pos = self.ik_node_pos_x
        self.ik_node_pos_x -= 3.5
        return [pos, 0]

    def add_ik(self, start_bone, end_bone=None):
        ik_data = IKData(self.character, start_bone, end_bone)
        KIN_chop = self.chopnet.createNode("inversekin", ik_data.KIN_name)

        IK_affector_ptr = utl.append_object_child_to(self.ik_controls_space_node, "null", ik_data.IK_affector_ptr_name)
        IK_affector_ptr.setDisplayFlag(False)
        IK_affector_ptr.move(self.ik_node_pos())
        IK_affector = utl.append_object_child_to(IK_affector_ptr, "null", ik_data.IK_affector_name)

        world_transform = hou.Matrix4(ik_data.end_bone.worldTransform().extractRotationMatrix3())
        end_bone_position = character_utils.get_bone_position(ik_data.end_bone)
        world_transform = world_transform * hou.hmath.buildTranslate((end_bone_position.x(), end_bone_position.y(), end_bone_position.z())) 
        IK_affector_ptr.setWorldTransform(world_transform)
        IK_affector_ptr.moveParmTransformIntoPreTransform() 
        self.controls_nodes.append(IK_affector)
        IK_affector.setParms({ "geoscale" : .15, "controltype" : 2 })
        IK_affector.parmTuple("dcolor").set((.9, 0, 0))

        IK_twist_ptr = utl.append_object_child_to(self.ik_controls_space_node, "null", ik_data.IK_twist_ptr_name)
        IK_twist_ptr.setDisplayFlag(False)
        IK_twist_ptr.move(self.ik_node_pos())
        IK_twist = utl.append_object_child_to(IK_twist_ptr, "null", ik_data.IK_twist_name)

        world_transform = ik_data.end_bone.worldTransform()
        IK_twist_ptr.setWorldTransform(world_transform)
        IK_twist_ptr.moveParmTransformIntoPreTransform() 
        IK_twist_ptr.parm(ik_data.IK_twist_offset_parm_name).set(IK_twist_ptr.parm(ik_data.IK_twist_offset_parm_name).eval() + ik_data.IK_twist_offset)
        IK_twist_ptr.moveParmTransformIntoPreTransform() 
        self.controls_nodes.append(IK_twist)
        IK_twist.setParms({ "geoscale" : .05, "controltype" : 1, "orientation" : 0})
        IK_twist.parmTuple("dcolor").set((.9, 0, 0))

        KIN_chop.setParms({ "solvertype" : 2, "iktwist" : ik_data.IK_twist_degrees, 
        "bonerootpath" : KIN_chop.relativePathTo(ik_data.start_bone), "boneendpath" : KIN_chop.relativePathTo(ik_data.end_bone),
        "endaffectorpath" : KIN_chop.relativePathTo(IK_affector), "twistaffectorpath" : KIN_chop.relativePathTo(IK_twist) })

        ik_data.start_bone.parm("solver").set(ik_data.start_bone.relativePathTo(KIN_chop))
        ik_data.end_bone.parm("solver").set(ik_data.end_bone.relativePathTo(KIN_chop))


        end_joint = ik_data.end_bone.outputConnections()[0].outputNode()
        blend = utl.append_object_child_to(end_joint, "blend", ik_data.blend_node_name)
        oriented_effector = utl.append_object_child_to(IK_affector, "null", ik_data.IK_affector_name + "_orient")
        oriented_effector.setWorldTransform(end_joint.worldTransform())
        oriented_effector.moveParmTransformIntoPreTransform()
        oriented_effector.setDisplayFlag(False)
        blend.setNextInput(oriented_effector)
        blend.setParms({"blendm1" : 455, "blendm2" : 56})
        blend.setPosition(end_joint.position())
        blend.move([4, 0])
        blend.setDisplayFlag(False)
        for con in end_joint.outputConnections():
            output_node = con.outputNode()
            if output_node != blend:
                output_node.setInput(0, blend)

        utl.lock_parms(IK_affector, ["scale"], ["s", "p"])
        utl.lock_parms(IK_twist, ["scale"], ["r", "s", "p"])

        # set world transform 
        # move to pretransform
        # color
        # setup display
        # TO DO custom pyramid display like in maya rig
        # TO DO display wrists as hand bounding box

        # copy 

    def ctrl_node_color(self):
        return hou.Color((0.0, .8, 1))

    def setup_character_transforms(self):
        
        self.master_input.setPosition(self.character.origin.position())
        self.master_input.move([0, 10])

        master_space_node = self.fbx.createNode("null", "master_space")
        master_space_node.setPosition(self.master_input.position())
        master_space_node.move([0, -1])
        master_space_node.setInput(0, self.master_input)
        master_space_node.setDisplayFlag(False)

        ctrl_master_node = utl.append_object_child_to(master_space_node, "null", "ctrl_master")
        ctrl_master_node.setParms({ "geoscale" : 2.0, "controltype" : 1, "orientation" : 2})
        
        local_master_node = utl.append_object_child_to(ctrl_master_node, "null", "local_master_space")
        local_master_node.setPreTransform(self.character.origin.worldTransform())
        local_master_node.setDisplayFlag(False)

        ctrl_local_master_node = utl.append_object_child_to(local_master_node, "null", "ctrl_local_master")
        ctrl_local_master_node.setParms({ "geoscale" : .75, "controltype" : 1, "orientation" : 2})
        self.character.origin.setPreTransform(hou.Matrix4(1))
        
        ik_controls_space = utl.append_object_child_to(ctrl_local_master_node, "null", "ik_controls_space")
        ik_controls_space.move([-2, 0])
        character_space = utl.append_object_child_to(ctrl_local_master_node, "null", "character_space")
        character_space.move([2, 0])
        ik_controls_space.setDisplayFlag(False)
        character_space.setDisplayFlag(False)

        ctrl_cog = utl.append_object_child_to(character_space, "null", "ctrl_cog")
        ctrl_cog.setParms({ "geoscale" : .85, "controltype" : 3, "orientation" : 2})

        # additional
        utl.lock_parms(ctrl_master_node, parm_tuple_names=["s", "p"])
        utl.lock_parms(ctrl_local_master_node, ["scale"], ["s", "p"])
        utl.lock_parms(ctrl_cog, ["scale"], ["s", "p"])

        self.controls_nodes.append(ctrl_master_node)
        self.controls_nodes.append(ctrl_local_master_node)
        self.controls_nodes.append(ctrl_cog)

        self.ik_controls_space_node = ik_controls_space
        self.character.origin.setInput(0, ctrl_cog)

def get_chopnet_in_character_subnet(subnet):
    chopnet = utl.nodetype_in_node(subnet, "chopnet")
    if not chopnet:
        geos = utl.nodetypes_in_node(subnet, "geo")
        geos.sort(key=lambda x: x.position()[1], reverse=False)
        chopnet = subnet.createNode("chopnet", "control_chops")
        chopnet.setPosition(geos[0].position())
        chopnet.move([0, -1])
    return chopnet

def add_character_controls(fbx=None):
    if not fbx:
        fbx = utl.find_raw_fbx_node()
    
    geos = utl.nodetypes_in_node(fbx, "geo")
    bones = utl.nodetypes_in_node(fbx, "bone") + utl.nodetypes_in_node(fbx, "null")
    if geos:
        for geo in geos:
            geo.setSelectableInViewport(False)
            
    if bones:
        for bone in bones:
            bone.setSelectableInViewport(False)
            bone.setDisplayFlag(False)
        
    character_manager = CharacterManager(fbx)
    character_manager.setup_controls()
    fbx.setSelectableInViewport(False)
