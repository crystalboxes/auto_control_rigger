import hou, utl

def make_compatible_fbx_hierarchy(character_subnet):
    character_subnet_children = character_subnet.children()
    nulls = utl.nodetypes_in_list(character_subnet_children, "null")
    geos = utl.nodetypes_in_list(character_subnet_children, "geo")
    target_nulls = []
    bones = []
    bone_name_map = {}
    old_to_new_map = {}

    # lock the current mesh deformation
    for geo in geos:
        geo.displayNode().setHardLocked(True)
        utl.nodetype_in_list(geo.children(), "captureoverride").setHardLocked(True)
        
    # move cregion sops into bones, break the rig (temporarily)
    # writes bone-null correspondance for further bone weight transfer
    for null in nulls:
        cregion = utl.nodetype_in_list(null.children(), "cregion")
        if cregion:
            children = []
            for child in null.outputConnections():
                children.append(child.outputNode())
            children = utl.nodetypes_in_list(children, "bone")
            
            if len(children) > 1:
                # this is for gathering nulls which have multple bone children
                # later on those bones will get a separate parent null 
                # to move the pretransform from the bone
                target_nulls.append(null)
                bones.extend(children)

            for child_bone in children:
                capt = hou.copyNodesTo([cregion], child_bone)[0]
                child_bone.displayNode().setInput(2, capt)
                bone_name_map[child_bone.name()] = null.name()
            old_to_new_map[null.name()] = children
            cregion.destroy()

    # for each bone with non-unique parent add control null
    for bone in bones:
        ctrl_null = bone.parent().createNode("null", bone.name() + "_ctrl")
        ctrl_null.setPosition(bone.position())
        ctrl_null.move([0, 1])
        ctrl_null.setNextInput(bone)
        ctrl_null.parm("keeppos").set(True)
        ctrl_null.setInput(0, None)
        bone.setPreTransform(hou.Matrix4(1))
        ctrl_null.setNextInput(bone.inputConnections()[0].inputNode())
        bone.setInput(0, ctrl_null)
        ctrl_null.parm("keeppos").set(False)
        ctrl_null.setDisplayFlag(False)

    # remove pre-transform from bones and move them to the parent nulls
    bones = utl.nodetypes_in_list(character_subnet_children, "bone")
    for bone in bones:
        world_transform = bone.worldTransform()
        bone.setPreTransform(hou.Matrix4(1))
        bone.inputConnections()[0].inputNode().setWorldTransform(world_transform)
        
    def ordered_bone_names_list(unpacked_attribs_node):
        # get capture paths
        attrib_vals = unpacked_attribs_node.geometry().stringListAttribValue("boneCapture_pCaptPath")
        bone_names = []
        for value in attrib_vals:
            name_parts = value.split("/")
            bone_name = ""
            for x in range(len(name_parts) - 1):
                bone_name += name_parts[x] + "/"
            bone_names.append(bone_name[:-1])
        return bone_names

    # re-capture with the new bones
    for geo in geos:
        capture_source_frozen = utl.nodetype_in_list(geo.children(), "capture")
        bc_names = capture_source_frozen.parm("extraregions").eval().split(" ")

        for x in range(len(bc_names)):
            bc_names[x] = bc_names[x].replace("../../", "")
            bc_names[x] = bc_names[x].replace("/cregion", "")

        capture_source = utl.nodetype_in_list(geo.children(), "captureoverride")
        unpacked_source = geo.createNode("captureattribunpack", "unpacked_source")
        unpacked_source.setNextInput(capture_source)
        source_bone_names_ordered = ordered_bone_names_list(unpacked_source)
        bones_parm_list = []
        for source_bone_name in source_bone_names_ordered:
            #if source_bone_name:
            bones_parm_list.extend(old_to_new_map[source_bone_name])
        
        capture = utl.append_sop_node(geo, "capture")
        parm_val = ""
        for bone in bones_parm_list:
            parm_val += "../../" + bone.name() + "/cregion "
        capture.parm("extraregions").set(parm_val)
        capture.setParms({"extraregions" : parm_val})

        unpacked_dst = utl.append_sop_node(geo, "captureattribunpack", "unpacked_source")
        dst_bone_names_ordered = ordered_bone_names_list(unpacked_dst)

        snippet = ""
        for idx, point in enumerate(unpacked_dst.geometry().points()):
        
            indices = []
            data = []

            unpacked_source_point = unpacked_source.geometry().iterPoints()[idx]
            source_indices = unpacked_source_point.intListAttribValue("boneCapture_index")
            source_data = unpacked_source_point.floatListAttribValue("boneCapture_data")
            for x in range(len(source_data)):
                weight = source_data[x]
                target_bone = source_bone_names_ordered[source_indices[x]]
                new_bones = old_to_new_map[target_bone]
                for new_bone in new_bones:
                    new_bone_name = new_bone.name()
                    new_bone_list_id = dst_bone_names_ordered.index(new_bone_name)
                    indices.append(new_bone_list_id)
                    data.append(weight)

            data_str = ""
            idx_str = ""
            for idx, d in enumerate(data):
                data_str += str(d) + ","
                idx_str += str(indices[idx]) + ","

            data_str = "array(" + data_str[:-1] + ")"
            idx_str = "array(" + idx_str[:-1] + ")"
            snippet += 'setpointattrib(geoself(), "boneCapture_data", ' + str(point.number()) + ", float[](" + data_str + "));"
            snippet += 'setpointattrib(geoself(), "boneCapture_index", ' + str(point.number()) + ", int[](" + idx_str + "));"
        
        attribwrangle = utl.append_sop_node(geo, "attribwrangle")
        attribwrangle.setNextInput(unpacked_dst)
        attribwrangle.setParms({ "class" : 0, "snippet" : snippet })

        utl.append_sop_node(geo, "captureattribpack")
        utl.append_sop_node(geo, "deform")
        unpacked_source.destroy()
