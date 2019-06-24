import hou, utl, capture_attributes

def get_bone_position(bone):
    bone_length = float(bone.parm("length").eval()) * float(bone.parm("scale").eval())
    
    fwd = bone.worldTransform().asTupleOfTuples()[2]
    forward = hou.Vector3(fwd[0], fwd[1], fwd[2]).normalized()
    origin = bone.origin()
    B = origin - forward * bone_length
    return B

def get_bone_list(subnet):
    if subnet:
        if subnet.type().name() == "subnet":
            return utl.nodetypes_in_list(subnet.children(), "bone")
    return []

def fix_bone_orientation(bone):
    current_xform = bone.worldTransform()
    bone.parm("lookatpath").set("")
    bone.setWorldTransform(current_xform)
    bone.moveParmTransformIntoPreTransform() 

def find_corresponding_bone_null(bone):
    target_null = None
    target_position = get_bone_position(bone)
    input_connections = bone.inputConnections()
    if input_connections:
        parent = input_connections[0].inputNode()
        children = []
        for c in parent.outputConnections():
            children.append(c.outputNode())
            
        children = utl.nodetypes_in_list(children, "null")
        for child in children:
            if child.origin().almostEqual(target_position):
                target_null = child
    return target_null

def reparent_fbx_bones(subnet):
    nulls = utl.nodetypes_in_list(subnet.children(), "null")
    for null in nulls:
        for parm in null.parms():
            parm.deleteAllKeyframes()
        null.moveParmTransformIntoPreTransform()
        
    bones = get_bone_list(subnet)
    
    for bone in bones:
        bone.parm("length").deleteAllKeyframes()
        target_null = find_corresponding_bone_null(bone)
        if target_null and not bone.outputConnections():
            fix_bone_orientation(bone)
            target_null.parm("keeppos").set(1)
            target_null.setInput(0, bone)
            target_null.parm("keeppos").set(0)

def capture_geo_cleanup(subnet):
    geos = utl.nodetypes_in_list(subnet.children(), "geo")
    for geo in geos:
        disp = geo.displayNode()
        unpacked = disp.inputConnections()[0].inputNode()
        unpacked.setHardLocked(True)
        for node in geo.children():
            if node not in [disp, unpacked]:
                node.destroy() 

def process_fbx_subnet():
    subnet = utl.find_raw_fbx_node()
    if subnet:
        reparent_fbx_bones(subnet)
        capture_attributes.make_compatible_fbx_hierarchy(subnet)
        capture_geo_cleanup(subnet)
    hou.ui.displayMessage("Finished")