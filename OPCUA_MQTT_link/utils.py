from opcua import Client, ua, Node
import hashlib
import datetime


def getTagname(node):
    path = node.nodeid.Identifier
    position = path.rfind(".")
    return path[position + 1 :]


def getNewHash(pObject):
    if "_timestamp" in pObject:
        del pObject["_timestamp"]
    newHash = hashlib.md5(pObject.__str__().encode("utf-8")).hexdigest()
    return newHash


def setTimestamp(pObject):
    pObject["_timestamp"] = str(datetime.datetime.now())
