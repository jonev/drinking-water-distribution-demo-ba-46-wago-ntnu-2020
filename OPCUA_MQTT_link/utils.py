from opcua import Client, ua, Node


def getTagname(node):
    path = node.nodeid.Identifier
    position = path.rfind(".")
    return path[position + 1 :]


def buildNodeTree(pObject, nodeStore, OpcNodes):
    for node in OpcNodes:
        children = node.get_children()
        tagname = getTagname(node)
        if len(children) == 0:
            if tagname.startswith("_"):
                pObject[tagname] = node.get_value()
            else:
                nodeStore[tagname] = node
                pObject[tagname] = node.get_value()
        else:
            nodeStore[tagname] = {}
            pObject[tagname] = {}
            buildNodeTree(pObject[tagname], nodeStore[tagname], children)


def getValuesFromNodes(pObject, nodeStore):
    for tagname, pObje in pObject.items():
        if tagname.startswith("_"):
            continue
        if type(pObje) is dict:
            getValuesFromNodes(pObje, nodeStore[tagname])
        else:
            pObject[tagname] = nodeStore[tagname].get_value()


def setValuesToNodes(pObject, nodeStore):
    for tagname, pObje in pObject.items():
        if tagname.startswith("_"):
            continue
        if type(pObje) is dict:
            setValuesToNodes(pObje, nodeStore[tagname])
        else:
            value = pObje
            node = nodeStore[tagname]
            if type(value) is str:
                node.set_value(value)
            elif type(value) is bool:
                node.set_value(value)
            elif type(value) is float:
                node.set_value(value, varianttype=ua.VariantType.Float)
            elif type(value) is int:
                node.set_value(value, varianttype=ua.VariantType.Int16)
            else:
                raise Exception("PLC: Type not found")
