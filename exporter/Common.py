'''
Common functions and utilities

(c) 2009 - 2015
    Balakrishnan Ranganathan (balki_live_com)
    All Rights Reserved.
'''

import os
import io
import sys
import re
import math
import shutil
import fnmatch
import datetime
import maya.cmds as Cmds
import maya.mel as Mel
import xml.dom.minidom as Dom
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

global InfiniteLoopCounter

def StartInfinity():
    global InfiniteLoopCounter
    InfiniteLoopCounter = 0
    
def CheckInfinity(infinity=1000):
    global InfiniteLoopCounter
    InfiniteLoopCounter = InfiniteLoopCounter + 1
    
    if InfiniteLoopCounter >= infinity:
        print 'Loop overboard!'
        return True
    
    return False

def Nop():
    return

def IsNoneOrEmpty(string):
    return string is None or len(string) == 0
    
def IsZero(vector):
    return vector[0] == 0 and vector[1] == 0 and vector[2] == 0
    
def IsOne(vector):
    return vector[0] == 1 and vector[1] == 1 and vector[2] == 1

class XmlWriter:
    fileIndentLevel = 0
    defFile = ""
    
    def __init__(self, defFile):
        self.defFile = defFile

    def PushIndentLevel(self):
        self.fileIndentLevel += 1
        
    def PopIndentLevel(self):
        self.fileIndentLevel -= 1
        
    def WriteSpaces(self):
        for i in range(self.fileIndentLevel):
            self.defFile.write("    ")

    def WriteAttribute(self, key, value):
        self.defFile.write(" %s=\"%s\" " % (key, value))

    def WriteStartElement(self, elementName):
        self.WriteSpaces()
        self.defFile.write("<%s>\n" % elementName)
        self.PushIndentLevel()
        
    def WriteEndElement(self, elementName):
        self.PopIndentLevel()
        self.WriteSpaces()
        self.defFile.write("</%s>\n" % elementName)

    def WriteElementStart(self, elementName):
        self.WriteSpaces()
        self.defFile.write("<%s" % elementName)
        
    def WriteElementEnd(self, endElement = False):
        if endElement == True:
            self.defFile.write("/>\n")
        else:
            self.defFile.write(">\n")
            self.PushIndentLevel()

    def WriteXYZElement(self, elementName, xyz):
        self.WriteElementStart(elementName)
        self.WriteAttribute("X", NaNToNumber(xyz[0], 0))
        self.WriteAttribute("Y", NaNToNumber(xyz[1], 0))
        self.WriteAttribute("Z", NaNToNumber(xyz[2], 0))
        self.WriteElementEnd(True)

    def WriteXYZWElement(self, elementName, xyzw):
        self.WriteElementStart(elementName)
        self.WriteAttribute("X", NaNToNumber(xyzw[0], 0))
        self.WriteAttribute("Y", NaNToNumber(xyzw[1], 0))
        self.WriteAttribute("Z", NaNToNumber(xyzw[2], 0))
        self.WriteAttribute("W", NaNToNumber(xyzw[3], 1))
        self.WriteElementEnd(True)
        
    def WriteMatrixElement(self, elementName, matrix):
        self.WriteElementStart(elementName)
        
        for row in range(4):
            for column in range(4):
                self.WriteAttribute("M%d%d" % (row, column), matrix(row, column))
        
        self.WriteElementEnd(True)
        
    def WriteValueElement(self, elementName, value):
        self.WriteElementStart(elementName)
        self.WriteAttribute("Value", value)
        self.WriteElementEnd(True)

def PrintXYZ(xyz):
    print "X", str(xyz[0]),
    print "Y", str(xyz[1]),
    print "Z", str(xyz[2])

def PrintXYZW(xyzw):
    print "X", str(xyzw[0]),
    print "Y", str(xyzw[1]),
    print "Z", str(xyzw[2]),
    print "W", str(xyzw[3])

def CreateXYZKey(xyz):
    key = "X" + str(xyz[0])
    key += "|Y" + str(xyz[1])
    key += "|Z" + str(xyz[2])
    return key

def CreateXYZWKey(xyzw):
    key = "X" + str(xyzw[0])
    key += "|Y" + str(xyzw[1])
    key += "|Z" + str(xyzw[2])
    key += "|W" + str(xyzw[3])
    return key
    
def IsNaN(value):
    return value != value;
    
def NaNToNumber(value, number):
    if IsNaN(value):
        return number
    else:
        return value

def GetConnectedPlugs(plug, incoming, outgoing):
    connectedPlugs = OpenMaya.MPlugArray()
    plug.connectedTo(connectedPlugs, incoming, outgoing)
    return connectedPlugs
    
def GetConnectedPlug(plug, connectedPlugName, connectedPlugType):
    connectedPlugs = OpenMaya.MPlugArray()
    plug.connectedTo(connectedPlugs, True, False)
    for k in range(connectedPlugs.length()):
        if connectedPlugs[k].node().apiType() == connectedPlugType and connectedPlugs[k].partialName(False, False, False, False, False, True) == connectedPlugName:
            return connectedPlugs[k]
    
    return OpenMaya.MPlug()

def PlugValueAsMVector(plug):
    if plug.numChildren() == 3:
        return OpenMaya.MVector(plug.child(0).asMAngle().asDegrees(), plug.child(1).asMAngle().asDegrees(), plug.child(2).asMAngle().asDegrees())
    else:
        return OpenMaya.MVector()
        
def VectorDegreesToRadians(vector):
    return OpenMaya.MVector(OpenMaya.MAngle(vector[0], OpenMaya.MAngle.kDegrees).asRadians(), OpenMaya.MAngle(vector[1], OpenMaya.MAngle.kDegrees).asRadians(), OpenMaya.MAngle(vector[2], OpenMaya.MAngle.kDegrees).asRadians())

def VectorRadiansToDegrees(vector):
    return OpenMaya.MVector(OpenMaya.MAngle(vector[0], OpenMaya.MAngle.kRadians).asDegrees(), OpenMaya.MAngle(vector[1], OpenMaya.MAngle.kRadians).asDegrees(), OpenMaya.MAngle(vector[2], OpenMaya.MAngle.kRadians).asDegrees())

def CreateTransformNodes(nodeName, xmlNode):
    '''
    Creates position, rotation and scale nodes for the node nodeName
    and attaches them to xmlNode
    '''
    print "Getting transform for", nodeName, Cmds.nodeType(nodeName)
    
    position = Cmds.xform(nodeName, q=True, t=True);
    rotation = Cmds.xform(nodeName, q=True, ro=True);
    scale = Cmds.xform(nodeName, q=True, s=True);
    
    if not IsZero(position):
        positionNode = xmlDocument.createElement("Position")
        xmlNode.appendChild(positionNode)
        positionNode.setAttribute("X", str(position[0]))
        positionNode.setAttribute("Y", str(position[1]))
        positionNode.setAttribute("Z", str(position[2]))
    
    if not IsZero(rotation):
        rotationNode = xmlDocument.createElement("Rotation")
        xmlNode.appendChild(rotationNode)
        rotationNode.setAttribute("X", str(rotation[0]))
        rotationNode.setAttribute("Y", str(rotation[1]))
        rotationNode.setAttribute("Z", str(rotation[2]))
    
    if not IsOne(scale):
        scaleNode = xmlDocument.createElement("Scale")
        xmlNode.appendChild(scaleNode)
        scaleNode.setAttribute("X", str(scale[0]))
        scaleNode.setAttribute("Y", str(scale[1]))
        scaleNode.setAttribute("Z", str(scale[2]))

def GetParentName(fullNodePath):
    '''
    Returns the parent's name
    '''
    return fullNodePath.split("|")[-2]

def Bake(minFrame, maxFrame):
    Cmds.bakeResults(sm=True, t=(minFrame, maxFrame), hi="below", sb=1, dic=True, pok=False, sac=False, ral=False, cp=False, shape=False)

def FindIndexOf(list, value, start=0, end=-1):
    '''
    Finds the first occurance of value in [start, end]
    '''
    if end == -1:
        end = len(list)
    
    i = start
    while i <= end:
        if list[i] == value:
            return i
        
        i = i + 1
    
    return end

'''
To cut and shift the keyframes based on MoveLister entries

import maya.cmds as Cmds;

Cmds.select(all=True)
Cmds.cutKey(time=(-1000, moveMin))
Cmds.cutKey(time=(moveMax, 10000))
Cmds.keyframe(e=True, r=True, timeChange=-moveMin, time=(moveMin, moveMax))

FbxExport(moveName)

Cmds.undo()
Cmds.undo()
Cmds.undo()
Cmds.undo()
'''

'''
To clean up the weights

import maya.cmds as Cmds;

skinMesh = "Knight_mesh"

# Find the skin cluster
skinCluster = None
histories = Cmds.listHistory(skinMesh, pdo=True);
for history in histories:
    if Cmds.nodeType(history) in ["skinCluster"]:
        skinCluster = history

if IsNoneOrEmpty(skinCluster):
    sys.exit()
    
joints = Cmds.skinCluster(skinMesh, q=True, inf=True)
vertices = Cmds.polyEvaluate(skinMesh, v=True)

for v in range(0, vertices):
    print v
    weights = Cmds.skinPercent(skinCluster, skinMesh + ".vtx[" + str(v) + "]", q=True, v=True)
    for i in range(0, len(weights)):
        if weights[i] > 1.0:
            print weights[i]
            weights[i] = 1.0
            print weights[i]
        if weights[i] < 0.0:
            weights[i] = 0
    
    tv = []
    for i in range(0, len(joints)):
        tv.append((joints[i], weights[i]))
    
    #Cmds.skinPercent(skinCluster, skinMesh + ".vtx[" + str(v) + "]", tv=tv)


'''

'''
addAttr -ln "PhysicsShape"  -at "enum" -en "Mesh:Hull:"  |Scene|Straight_City_Street:Straight_City_Street;
setAttr -e-keyable true |Scene|Straight_City_Street:Straight_City_Street.PhysicsShape;
'''

'''
To use this in the shelf

import AnimationDefExporter as Ade
reload(Ade)
Ade.Run()
'''

'''
To create material custom nodes

import AnimationDefExporter as Ade
reload(Ade)
Ade.Run(False, False)
'''

'''
inputPlug = skinCluster.findPlug("input")
childPlug = inputPlug.elementByLogicalIndex(0)

geometryPlug = childPlug.child(0)
geometryObject = geometryPlug.asMObject()
mesh.setObject(geometryObject)

ProcessModel(mesh, instanceNumber, modelMeshesXmlElement, export)
'''

'''
No flatten transforms

Create fake weightedvertex if none
Attach to root

'''

'''
Name1: Mat_House031.outColor kPhong
Name1: Mat_House031.message kPhong
Name1: Mat_House031.color kPhong
  Name2: AHouse2_tga.outColor kFileTexture
Name1: Mat_House031.normalCamera kPhong
  Name2: bump2d1.outNormal kBump
   Dep node: bump2d1
    Bump parent node: bump2d1.message kBump
    Bump parent node: bump2d1.bumpValue kBump
      Bump node: AHouse2_N_tga.outAlpha kFileTexture
    Bump parent node: bump2d1.outNormal kBump
Name1: Mat_House031.specularColor kPhong
  Name2: AHouse2_S_tga.outColor kFileTexture
'''

'''
connectionsPlugArray = OpenMaya.MPlugArray()
lambertShader.getConnections(connectionsPlugArray)
for j in range(connectionsPlugArray.length()):
    connectedPlugs = OpenMaya.MPlugArray()
    connectionsPlugArray[j].connectedTo(connectedPlugs, True, False)
    print "Name1:", connectionsPlugArray[j].name(), connectionsPlugArray[j].node().apiTypeStr()
    for k in range(connectedPlugs.length()):
        print "  Name2:", connectedPlugs[k].name(), connectedPlugs[k].node().apiTypeStr()
        if (connectedPlugs[k].node().apiType() == OpenMaya.MFn.kFileTexture):
            material.TextureFilename = GetFileTextureName(connectedPlugs[k])
        elif (connectedPlugs[k].node().apiType() == OpenMaya.MFn.kBump):
            bumpDepNode = OpenMaya.MFnDependencyNode(connectedPlugs[k].node())
            print "   Dep node:", bumpDepNode.name()
            cpa = OpenMaya.MPlugArray()
            bumpDepNode.getConnections(cpa)
            for l in range(cpa.length()):
                cp = OpenMaya.MPlugArray()
                cpa[l].connectedTo(cp, True, False)
                print "    Bump parent node:", cpa[l].name(), cpa[l].node().apiTypeStr()
                for m in range(cp.length()):
                    if (cp[m].node().apiType() == OpenMaya.MFn.kFileTexture):
                        print "      Bump node:", cp[m].name(), cp[m].node().apiTypeStr()
                        material.NormalMapFilename = GetFileTextureName(cp[m])
'''

'''
angleRadians =  OpenMaya.MAngle(90, OpenMaya.MAngle.kDegrees).asRadians()
print "Angle Radians: ", angleRadians
euler = OpenMaya.MEulerRotation(0, 0, angleRadians)
print "Euler: ",
PrintXYZ(euler)

quat = euler.asQuaternion()
print "Quat: ",
PrintXYZW(quat)

euler2 = quat.asEulerRotation()
print "Euler radians?: ", euler2[0], euler2[1], euler2[2]
print "Euler degrees: ", 
PrintXYZ(VectorRadiansToDegrees(euler2))
'''

'''
print joint.Name
print "Euler: ",
print PrintXYZ(VectorRadiansToDegrees(joint.Rotation.asEulerRotation()))

joint.Rotation = joint.Rotation * jointOrientRotation

print "Euler: ",
print PrintXYZ(VectorRadiansToDegrees(joint.Rotation.asEulerRotation()))

break
'''

'''
connectionsPlugArray = OpenMaya.MPlugArray()
lambertShader.getConnections(connectionsPlugArray)
for j in range(connectionsPlugArray.length()):
    connectedPlugs = OpenMaya.MPlugArray()
    connectionsPlugArray[j].connectedTo(connectedPlugs, True, False)
    print "Name1:", connectionsPlugArray[j].name(), connectionsPlugArray[j].node().apiTypeStr()
    for k in range(connectedPlugs.length()):
        _connectedPlugs = OpenMaya.MPlugArray()
        connectedPlugs[k].connectedTo(_connectedPlugs, True, False)
        print "  Name2:", connectedPlugs[k].name(), connectedPlugs[k].node().apiTypeStr()
        for l in range(_connectedPlugs.length()):
            print "  Name3:", _connectedPlugs[l].name(), _connectedPlugs[l].node().apiTypeStr()
'''