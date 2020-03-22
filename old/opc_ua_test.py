from opcua import Client, ua
import time

client = Client("opc.tcp://192.168.0.15:4840")
client.set_user("admin")
client.set_password("wago")
ns = 4
HmiId = "|var|WAGO 750-8214 PFC200 G2 2ETH RS CAN.PFCx00_SmartCoupler.HMI"
variables = {}


def getChildrenRecursive(child):
    children = child.get_children()
    if len(children) == 0:
        variables[child.nodeid.Identifier.replace(HmiId + ".", "")] = child
    else:
        for c in children:
            getChildrenRecursive(c)


try:
    client.connect()
    # client.load_type_definitions()
    # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
    root = client.get_root_node()
    print("Objects node is: ", root)

    # Node objects have methods to read and write node attributes as well as browse or populate address space
    children = root.get_children()
    print("Children of root are: ", children)

    # get a specific node knowing its node id
    # var = client.get_node(ua.NodeId(86, 1))

    HMI = client.get_node("ns=" + str(ns) + ";s=" + HmiId)
    var = HMI.get_children()

    for child in HMI.get_children():
        getChildrenRecursive(child)

    print(variables["Motor1.startCommand"].get_value())
    variables["Motor1.startCommand"].set_value(False)
    print(variables["Motor1.startCommand"].get_value())
    print(variables["Motor1.stopCommand"].get_value())
    print(variables["Motor1.stopCommand"].set_value(False))
    print(variables["Motor1.setpoint"].get_value())
    print(variables["Motor1.setpoint"])
    variables["Motor1.setpoint"].set_value(20.0, varianttype=ua.VariantType.Float)
    print(variables["Motor1.setpoint"].get_value())
    scan = 0
    while scan < 100:
        scan = scan + 1
        variables["Motor1.setpoint"].set_value(1.0 + scan, varianttype=ua.VariantType.Float)
        time.sleep(4)
    # for nodeId, node in variables.items():
    #    print(str(nodeId) + " has value: " + str(node.get_value()))

finally:
    client.disconnect()
