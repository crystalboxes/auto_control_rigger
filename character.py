import utl

class Character:
    def __init__(self, character_subnet):
        bones = utl.nodetypes_in_node(character_subnet, "bone")
        nulls = utl.nodetypes_in_node(character_subnet, "null")

        self.origin = self.find_origin(nulls)

        self.Hips = self.find_bone_by_name_id("Hips_bone", bones)
        self.Spine = self.find_bone_by_name_id("Spine_bone", bones)
        self.Spine1 = self.find_bone_by_name_id("Spine1_bone", bones)
        self.Spine2 = self.find_bone_by_name_id("Spine2_bone", bones)
        self.Neck = self.find_bone_by_name_id("Neck_bone", bones)
        self.Head = self.find_bone_by_name_id("Head_bone", bones)
        self.Spine2_1 = self.find_bone_by_name_id("Spine2_bone1", bones)
        self.LeftShoulder = self.find_bone_by_name_id("LeftShoulder_bone", bones)
        self.LeftArm = self.find_bone_by_name_id("LeftArm_bone", bones)
        self.LeftForeArm = self.find_bone_by_name_id("LeftForeArm_bone", bones)
        self.LeftHand = self.find_bone_by_name_id("LeftHand_bone", bones)
        self.LeftHandThumb1 = self.find_bone_by_name_id("LeftHandThumb1_bone", bones)
        self.LeftHandThumb2 = self.find_bone_by_name_id("LeftHandThumb2_bone", bones)
        self.LeftHandThumb3 = self.find_bone_by_name_id("LeftHandThumb3_bone", bones)
        self.LeftHand_1 = self.find_bone_by_name_id("LeftHand_bone1", bones)
        self.LeftHandIndex1 = self.find_bone_by_name_id("LeftHandIndex1_bone", bones)
        self.LeftHandIndex2 = self.find_bone_by_name_id("LeftHandIndex2_bone", bones)
        self.LeftHandIndex3 = self.find_bone_by_name_id("LeftHandIndex3_bone", bones)
        self.LeftHand_2 = self.find_bone_by_name_id("LeftHand_bone2", bones)
        self.LeftHandMiddle1 = self.find_bone_by_name_id("LeftHandMiddle1_bone", bones)
        self.LeftHandMiddle2 = self.find_bone_by_name_id("LeftHandMiddle2_bone", bones)
        self.LeftHandMiddle3 = self.find_bone_by_name_id("LeftHandMiddle3_bone", bones)
        self.LeftHand_3 = self.find_bone_by_name_id("LeftHand_bone3", bones)
        self.LeftHandRing1 = self.find_bone_by_name_id("LeftHandRing1_bone", bones)
        self.LeftHandRing2 = self.find_bone_by_name_id("LeftHandRing2_bone", bones)
        self.LeftHandRing3 = self.find_bone_by_name_id("LeftHandRing3_bone", bones)
        self.LeftHand_4 = self.find_bone_by_name_id("LeftHand_bone4", bones)
        self.LeftHandPinky1 = self.find_bone_by_name_id("LeftHandPinky1_bone", bones)
        self.LeftHandPinky2 = self.find_bone_by_name_id("LeftHandPinky2_bone", bones)
        self.LeftHandPinky3 = self.find_bone_by_name_id("LeftHandPinky3_bone", bones)
        self.Spine2_2 = self.find_bone_by_name_id("Spine2_bone2", bones)
        self.RightShoulder = self.find_bone_by_name_id("RightShoulder_bone", bones)
        self.RightArm = self.find_bone_by_name_id("RightArm_bone", bones)
        self.RightForeArm = self.find_bone_by_name_id("RightForeArm_bone", bones)
        self.RightHand = self.find_bone_by_name_id("RightHand_bone", bones)
        self.RightHandThumb1 = self.find_bone_by_name_id("RightHandThumb1_bone", bones)
        self.RightHandThumb2 = self.find_bone_by_name_id("RightHandThumb2_bone", bones)
        self.RightHandThumb3 = self.find_bone_by_name_id("RightHandThumb3_bone", bones)
        self.RightHand_1 = self.find_bone_by_name_id("RightHand_bone1", bones)
        self.RightHandIndex1 = self.find_bone_by_name_id("RightHandIndex1_bone", bones)
        self.RightHandIndex2 = self.find_bone_by_name_id("RightHandIndex2_bone", bones)
        self.RightHandIndex3 = self.find_bone_by_name_id("RightHandIndex3_bone", bones)
        self.RightHand_2 = self.find_bone_by_name_id("RightHand_bone2", bones)
        self.RightHandMiddle1 = self.find_bone_by_name_id("RightHandMiddle1_bone", bones)
        self.RightHandMiddle2 = self.find_bone_by_name_id("RightHandMiddle2_bone", bones)
        self.RightHandMiddle3 = self.find_bone_by_name_id("RightHandMiddle3_bone", bones)
        self.RightHand_3 = self.find_bone_by_name_id("RightHand_bone3", bones)
        self.RightHandRing1 = self.find_bone_by_name_id("RightHandRing1_bone", bones)
        self.RightHandRing2 = self.find_bone_by_name_id("RightHandRing2_bone", bones)
        self.RightHandRing3 = self.find_bone_by_name_id("RightHandRing3_bone", bones)
        self.RightHand_4 = self.find_bone_by_name_id("RightHand_bone4", bones)
        self.RightHandPinky1 = self.find_bone_by_name_id("RightHandPinky1_bone", bones)
        self.RightHandPinky2 = self.find_bone_by_name_id("RightHandPinky2_bone", bones)
        self.RightHandPinky3 = self.find_bone_by_name_id("RightHandPinky3_bone", bones)
        self.Hips_1 = self.find_bone_by_name_id("Hips_bone1", bones)
        self.LeftUpLeg = self.find_bone_by_name_id("LeftUpLeg_bone", bones)
        self.LeftLeg = self.find_bone_by_name_id("LeftLeg_bone", bones)
        self.LeftFoot = self.find_bone_by_name_id("LeftFoot_bone", bones)
        self.LeftToeBase = self.find_bone_by_name_id("LeftToeBase_bone", bones)
        self.Hips_2 = self.find_bone_by_name_id("Hips_bone2", bones)
        self.RightUpLeg = self.find_bone_by_name_id("RightUpLeg_bone", bones)
        self.RightLeg = self.find_bone_by_name_id("RightLeg_bone", bones)
        self.RightFoot = self.find_bone_by_name_id("RightFoot_bone", bones)
        self.RightToeBase = self.find_bone_by_name_id("RightToeBase_bone", bones)

    def find_bone_by_name_id(self, name_id, bones):
        for bone in bones:
            if name_id in bone.name():
                return bone
        return None

    def find_origin(self, nulls):
        for null in nulls:
            if "Hips" in null.name() and not null.inputConnections():
                return null
        return None
        