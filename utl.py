import hou

def nodetypes_in_node(node, type_name):
    if node:
        return nodetypes_in_list(node.children(), type_name)
    return []

def nodetypes_in_list(node_list, type_name):
    nodes = []
    for node in node_list:
        if node.type().name() == type_name:
            nodes.append(node)
    return nodes

def nodetype_in_node(node, type_name):
    if node:
        return nodetype_in_list(node.children(), type_name)
    return None

def nodetype_in_list(node_list, type_name):
    for node in node_list:
        if node.type().name() == type_name:
            return node
    return None

def selected_node():
    selected_node = None
    if hou.selectedNodes():
        selected_node = hou.selectedNodes()[0]
    return selected_node

def append_sop_node(geo, typename, name=""):
    if geo.type().name() != "geo":
        return None

    if not name:
        name = typename
    node = geo.createNode(typename, name)
    node.setPosition(geo.displayNode().position())
    node.move([0, -1])
    node.setNextInput(geo.displayNode())
    node.setDisplayFlag(True)
    node.setRenderFlag(True)
    return node

def append_object_child_to(node, typename, name=""):
    parent_node = node.parent()
    if parent_node.childTypeCategory().name() != "Object":
        return None

    new_node = parent_node.createNode(typename, name)
    new_node.setNextInput(node)
    new_node.setDisplayFlag(True)
    new_node.setPosition(node.position())
    new_node.move([0, -1])
    return new_node

def lock_parms(node, parm_names=[], parm_tuple_names=[]):
    for parm_name in parm_names:
        parm = node.parm(parm_name)
        if parm:
            parm.lock(True)
    for parm_tuple_name in parm_tuple_names:
        parm_tuple = node.parmTuple(parm_tuple_name)
        if parm_tuple:
            parm_tuple.lock(tuple([True] * len(parm_tuple)))

def find_raw_fbx_node():
    node = None
    pane_node = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).pwd()
    sel = selected_node()

    if pane_node.type().name() == "subnet":
        node = pane_node
    elif sel: 
        if sel.type().name() == "subnet":
            node = sel

    if node:
        if nodetypes_in_node(node, "bone"):
            return node

    hou.ui.displayMessage("The selected subnet is not valid.")
    return None

