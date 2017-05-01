'''
Scene Exporter for Maya

(c) 2009 - 2011
    Balakrishnan Ranganathan (balki_live_com)
    Rahul Singh (goobers.2_live_com)
All Rights Reserved.
'''

import os
import re
import math
import maya.cmds as Cmds
import maya.OpenMaya as OpenMaya
import maya.mel as Mel
import xml.dom.minidom as Dom
import inspect as Inspect

from Common import *

import ModelDefExporter as Mde
reload(Mde)

global xmlDocument
global exportPath
global exportModels

class PhysicsShapeEnum:
    Null = 0
    Mesh = 1
    Hull = 2
    
def PhysicsShapeEnumName(value):
    for namevalue in Inspect.getmembers(PhysicsShapeEnum):
        _name = namevalue[0]
        _value = namevalue[-1]
        if type(_value) == int and _value == value:
            return _name
    
    return "Null"

def PhysicsShapeEnumValue(name):
    for namevalue in Inspect.getmembers(PhysicsShapeEnum):
        _name = namevalue[0]
        _value = namevalue[-1]
        if type(_value) == int and _name == name:
            return _value
    
    return PhysicsShapeEnum.Null

def ParseVector3(xmlNode, nodeName, attributeString):
    '''
    Parses the vector3 xyz components and adds it to the xmlNode
    '''
    xmlNode.setAttribute("X", CleanAttribute(Cmds.getAttr(nodeName + "." + attributeString + "X")))
    xmlNode.setAttribute("Y", CleanAttribute(Cmds.getAttr(nodeName + "." + attributeString + "Y")))
    xmlNode.setAttribute("Z", CleanAttribute(Cmds.getAttr(nodeName + "."  + attributeString + "Z")))

def ParseQuaternion(xmlNode, nodeName, attributeString):
    '''
    Parses the vector3 xyz components and adds it to the xmlNode
    '''
    xmlNode.setAttribute("X", str(Cmds.getAttr(nodeName + "." + attributeString + "X")))
    xmlNode.setAttribute("Y", str(Cmds.getAttr(nodeName + "." + attributeString + "Y")))
    xmlNode.setAttribute("Z", str(Cmds.getAttr(nodeName + "."  + attributeString + "Z")))
    xmlNode.setAttribute("W", str(Cmds.getAttr(nodeName + "."  + attributeString + "W")))

def ParseColor(xmlNode, nodeName, attributeString = "color"):
    '''
    Parses the color rgba components and adds it to the xmlNode
    '''
    xmlNode.setAttribute("R", str(Cmds.getAttr(nodeName + "." + attributeString + "R")))
    xmlNode.setAttribute("G", str(Cmds.getAttr(nodeName + "." + attributeString + "G")))
    xmlNode.setAttribute("B", str(Cmds.getAttr(nodeName + "."  + attributeString + "B")))
    xmlNode.setAttribute("A", str(Cmds.getAttr(nodeName + ".intensity")))

def ParseMatrix(xmlNode, nodeName, attributeString):
    '''
    Parses the matrix and adds it to the xmlNode
    '''
    matrix = Cmds.getAttr(nodeName + "." + attributeString)
    for i in range(0, 16):
        xmlNode.setAttribute("v" + str(i), str(matrix[i]))

def ParseBoolean(booleanResult):
    '''
    Returns True for 1 and False for 0
    '''
    if (str(booleanResult) == "1"):
        return "true"
    else:
        return "false"

def CleanAttribute(attribute):
    '''
    Cleans up the random erroneous Maya attribute which comes in as a list
    and also makes all values a string to write to the XML file
    '''
    if (type(attribute) == type([])):
        attribute = attribute[-1]
    return str(attribute)

def GetParentName(fullNodePath):
    '''
    Returns the parent's name
    '''
    return fullNodePath.split("|")[-2]

def Traverse(node, parentXmlNode):
    '''
    Traverse the maya full-path node and attach it to the parentXmlNode
    '''
    global xmlDocument
    global exportModels
    
    children = Cmds.listRelatives([node], children=True)
    parent = Cmds.listRelatives([node], parent=True)

    '''
    print "\nNode: " + str(node)
    print "Children: " + str(children)
    print "Node type: " + Cmds.nodeType(node)
    print "Attributes: " + str(Cmds.listAttr(node))
    '''

    nodeName = node.split("|")[-1]
    nodeType = Cmds.nodeType(node)
    
    # xmlNode.setAttribute("", Cmds.getAttr(nodeName + "."))

    if nodeType in ["node", "transform"]:
        reference = False
        xmlNode = xmlDocument.createElement("FixtureXml")
        xmlNode.setAttribute("Name", nodeName)
    
        if nodeName.find(":") != -1:
            reference = True
            modelName = os.path.basename(Cmds.referenceQuery(nodeName, filename = True))
            modelName = os.path.splitext(modelName)[0]
            modelType = os.path.dirname(Cmds.referenceQuery(nodeName, filename = True))
            contentIndex = modelType.find("Content")
            if contentIndex == -1:
                print("Warning: Content doesn't seem to be in the right path")
            contentIndex += 8
            modelType = modelType[contentIndex:]
            #modelType = os.path.split(modelType)[-1]
        else:
            modelName = nodeName
            modelType = "Unknown"
      
        xmlNode.setAttribute("ModelName", modelName)
        xmlNode.setAttribute("ModelType", modelType)
        
        position = [0, 0, 0]
        if reference == False:
            '''
            Cmds.makeIdentity(nodeName, t=True, r=True, s=True, a=True)
            Cmds.xform(nodeName, cp=True)
            '''
            
            #position = Cmds.xform(nodeName, q=True, rp=True);
            
            #Temporary, under new reference setup
            position[0] = Cmds.getAttr(nodeName + ".translateX");
            position[1] = Cmds.getAttr(nodeName + ".translateY");
            position[2] = Cmds.getAttr(nodeName + ".translateZ");
        else:
            position[0] = Cmds.getAttr(nodeName + ".translateX");
            position[1] = Cmds.getAttr(nodeName + ".translateY");
            position[2] = Cmds.getAttr(nodeName + ".translateZ");
        
        rotation = Cmds.xform(nodeName, q=True, ro=True);
        scale = Cmds.xform(nodeName, q=True, s=True);
        
        # Rotation quaternion stuff
        matrixList = Cmds.getAttr(nodeName + ".worldMatrix")
        matrix = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(matrixList, matrix)
        rotationQuaternion = OpenMaya.MQuaternion()
        rotationQuaternion.assign(matrix)
        
        if reference == False:
            '''
            Cmds.xform(nodeName, r=True, rp=(0, -position[1], 0))
            Cmds.xform(nodeName, r=True, sp=(0, -position[1], 0))
            position = Cmds.xform(nodeName, q=True, rp=True);
            Cmds.delete(all=True, ch=True)
            '''
        
        positionNode = xmlDocument.createElement("Position")
        xmlNode.appendChild(positionNode)
        positionNode.setAttribute("X", str(position[0]))
        positionNode.setAttribute("Y", str(position[1]))
        positionNode.setAttribute("Z", str(position[2]))
        
        rotationNode =  xmlDocument.createElement("Rotation")
        xmlNode.appendChild(rotationNode)
        rotationNode.setAttribute("X", str(rotation[0]))
        rotationNode.setAttribute("Y", str(rotation[1]))
        rotationNode.setAttribute("Z", str(rotation[2]))
        
        rotationQuaternionNode =  xmlDocument.createElement("RotationQuaternion")
        xmlNode.appendChild(rotationQuaternionNode)
        rotationQuaternionNode.setAttribute("X", str(rotationQuaternion[0]))
        rotationQuaternionNode.setAttribute("Y", str(rotationQuaternion[1]))
        rotationQuaternionNode.setAttribute("Z", str(rotationQuaternion[2]))
        rotationQuaternionNode.setAttribute("W", str(rotationQuaternion[3]))
        
        scaleNode = xmlDocument.createElement("Scale")
        xmlNode.appendChild(scaleNode)
        scaleNode.setAttribute("X", str(scale[0]))
        scaleNode.setAttribute("Y", str(scale[1]))
        scaleNode.setAttribute("Z", str(scale[2]))
        
        # Physics shape custom data
        attributeName = nodeName + ".PhysicsShape"
        if not Cmds.objExists(attributeName):
            Cmds.addAttr(nodeName, longName="PhysicsShape", at="enum", en="Null:Mesh:Hull:", keyable=True)
            Cmds.setAttr(attributeName, PhysicsShapeEnum.Hull)
        attributeValue = Cmds.getAttr(attributeName)
        xmlNode.setAttribute("PhysicsShape", PhysicsShapeEnumName(attributeValue))
        
        # Lightmap custom data
        lightmapPath = ""
        directoryName = os.path.dirname(Cmds.file(q=True, sn=True))
        lightmapDirectory = "%s/renderData/mentalray/lightMap" % (directoryName)
        for file in os.listdir(lightmapDirectory):
            if fnmatch.fnmatch(file, 'Lightmap-%s*.*' % (modelName)):
                lightmapPath = "%s/%s" % (lightmapDirectory, file)
                contentIndex = lightmapPath.find("Content")
                if contentIndex == -1:
                    print("Warning: Content doesn't seem to be in the right path")
                contentIndex += 8
                lightmapPath = os.path.splitext(lightmapPath[contentIndex:])[0]
                break
        xmlNode.setAttribute("LightmapPath", lightmapPath)
    elif nodeType in ["pointLight", "directionalLight", "spotLight"]:
        xmlNode = xmlDocument.createElement("Light")
        xmlNode.setAttribute("Name", GetParentName(node))
        xmlNode.setAttribute("Type", nodeType.replace("Light", ""))

        xmlNode.setAttribute("Visible", ParseBoolean(Cmds.getAttr(GetParentName(node) + ".visibility")))
        xmlNode.setAttribute("CastShadows", ParseBoolean(Cmds.getAttr(nodeName + ".useDepthMapShadows")))

        if (Cmds.getAttr(nodeName + ".emitDiffuse") == 1):
            xmlColourDiffuseNode = xmlDocument.createElement("ColourDiffuse")
            xmlNode.appendChild(xmlColourDiffuseNode)
            ParseColor(xmlColourDiffuseNode, nodeName, "color") # Might be lightIntensity

        if (Cmds.getAttr(nodeName + ".emitSpecular") == 1):
            xmlColourSpecularNode = xmlDocument.createElement("ColourSpecular")
            xmlNode.appendChild(xmlColourSpecularNode)
            ParseColor(xmlColourSpecularNode, nodeName, "color") # Might be lightIntensity

        if nodeType in ["directionalLight", "spotLight"]:
            xmlNormalNode = xmlDocument.createElement("Normal")
            xmlNode.appendChild(xmlNormalNode)
            ParseVector3(xmlNormalNode, nodeName, "lightDirection")

        if nodeType == "spotLight":
            xmlLightRangeNode = xmlDocument.createElement("LightRange")
            xmlLightRangeNode.setAttribute("Inner", str(Cmds.getAttr(nodeName + ".coneAngle")))
            xmlLightRangeNode.setAttribute("Outer", str(Cmds.getAttr(nodeName + ".penumbraAngle")))
            xmlLightRangeNode.setAttribute("Falloff", str(Cmds.getAttr(nodeName + ".dropoff")))
            xmlNode.appendChild(xmlLightRangeNode)
        
        '''
        xmlLightAttenuationNode = xmlDocument.createElement("lightAttenuation")
        xmlLightAttenuationNode.appendChild(xmlLightAttenuationNode)
        xmlLightAttenuationNode.setAttribute("range", str(10000))
        if Cmds.getAttr(nodeName + ".decayRate") == 0:
            xmlLightAttenuationNode.setAttribute("constant", str(1))
        else:
            xmlLightAttenuationNode.setAttribute("constant", str(0))
            if Cmds.getAttr(nodeName + ".decayRate") == 1:
                xmlLightAttenuationNode.setAttribute("linear", str(1))
          else:
            xmlLightAttenuationNode.setAttribute("linear", str(0))
            if Cmds.getAttr(nodeName + ".decayRate") == 2:
                xmlLightAttenuationNode.setAttribute("quadratic", str(1))
            else:
                xmlLightAttenuationNode.setAttribute("quadratic", str(0))
        '''
    elif nodeType in ["camera"]:
        xmlNode = xmlDocument.createElement("Camera")
        xmlNode.setAttribute("Name", GetParentName(node))

        focalLength = Cmds.getAttr(nodeName + ".focalLength");
        aspectX = Cmds.getAttr(nodeName + ".horizontalFilmAperture")
        aspectY = Cmds.getAttr(nodeName + ".verticalFilmAperture")

        fovY = 0.0

        '''
        fovY = 2 * math.atan((aspectX/aspectY) / 2 * focalLength)
        #37.8 = 2 * math.atan(d / 2 * focalLength)
        #tan(37.8 / 2) * 2f = d
        #fovY = 2 * focalLength * math.tan((37.8 * math.pi / 180) / 2) # 23.96 for 37.8 (v) and 35.97 for 54.4 (h)
        fovY = fovY * 180.0 / math.pi
        '''

        fovY = 37.8

        xmlNode.setAttribute("fov", str(fovY))
        xmlNode.setAttribute("aspectRatio", str(aspectX / aspectY))

        if (Cmds.getAttr(nodeName + ".orthographic") == 0):
            xmlNode.setAttribute("projectionType", "perspective")
        else:
            xmlNode.setAttribute("projectionType", "orthographic")

        xmlClippingNode = xmlDocument.createElement("clipping")
        xmlNode.appendChild(xmlClippingNode)
        xmlClippingNode.setAttribute("nearPlaneDist", str(Cmds.getAttr(nodeName + ".nearClipPlane")))
        xmlClippingNode.setAttribute("farPlaneDist", str(Cmds.getAttr(nodeName + ".farClipPlane")))

        '''
        xmlLookTargetNode = xmlDocument.createElement("lookTarget")
        xmlNode.appendChild(xmlLookTargetNode)

        xmlTrackTargetNode = xmlDocument.createElement("trackTarget")
        xmlNode.appendChild(xmlTrackTargetNode)
        '''
    elif nodeType in ["joint"]:
        xmlNode = xmlDocument.createElement("Joint")
        xmlNode.setAttribute("Name", nodeName)
    elif nodeType in ["mesh"]:
        '''
        parentName = GetParentName(node)
        position = Cmds.xform(parentName, q=True, rp=True);
        
        Cmds.select(parentName, r=True)
        Cmds.selectKey(clear=True)
        Cmds.parent(w=True)
        Cmds.move(-position[0], -position[1], -position[2], a=True, worldSpace=True)
        Cmds.makeIdentity(t=True, r=True, s=True, a=True)
        Cmds.polyQuad(a=30, kgb=True, ktb=True, khe=True, ws=True, ch=True)
        Cmds.delete(all=True, ch=True)
        '''

        xmlNode = xmlDocument.createElement("Entity")
        xmlNode.setAttribute("Name", nodeName)

        '''
        Cmds.select(nodeName)
        # ToDo. This if check is temporary.
        if exportModels == True:
            Mde.Run(True, exportModels)

        Cmds.parent(parentName, "Scene")
        Cmds.move(position[0], position[1], position[2], a=True, worldSpace=True)
        Cmds.makeIdentity(t=True, r=True, s=True, a=True)
        Cmds.delete(all=True, ch=True)
        '''
    else:
        xmlNode = xmlDocument.createElement("FixtureXml")
        xmlNode.setAttribute("Name", nodeName)

    xmlNode.setAttribute("maya-type", nodeType)
    parentXmlNode.appendChild(xmlNode)

    if children != None:
        xmlChildrenNode = xmlDocument.createElement("Fixtures")
        xmlNode.appendChild(xmlChildrenNode)
        for child in children:
            Traverse(node + "|" + child, xmlChildrenNode)

def Run(export = False):
    global xmlDocument
    global exportPath
    global exportModels

    directoryName = os.path.dirname(Cmds.file(q=True, sn=True))
    filename = os.path.splitext(os.path.basename(Cmds.file(q=True, sn=True)))[0]
    filePath = "%s/%s.xml" % (directoryName, filename)
    exportModels = export;
    
    xmlDocument = Dom.Document()
    rootXmlElement = xmlDocument.createElement("FixtureXml")
    rootXmlElement.setAttribute("version", "1.1")
    xmlDocument.appendChild(rootXmlElement)

    xmlNodesElement = xmlDocument.createElement("Fixtures")
    rootXmlElement.appendChild(xmlNodesElement)

    rootNode = u"|Scene"
    if not Cmds.objExists(rootNode):
        rootNode = u"|scene"

    if not Cmds.objExists(rootNode):
        print "\n\nError: Please provide a root node (group) in maya named 'Scene' so the exporter can know what objects to export."
        Cmds.confirmDialog(title="Fixture Exporter for Maya", message="Please provide a root node (group) in maya named 'Scene' so the exporter can know what objects to export.", button=["Ooh!"])
    else:
        #exportPath = os.path.dirname(filePath) + "\\Fixtures"
        #if not os.path.exists(exportPath):
        #  os.mkdir(exportPath)
        #exportPath = exportPath.replace("\\", "\\\\")

        Cmds.makeIdentity(rootNode, t=False, r=False, s=True, a=True)
        Traverse(rootNode, xmlNodesElement)
        rootXmlElement.writexml(open(filePath, "w"), "", "\t", "\n")
        print "\n\n\nExport complete."
        Cmds.confirmDialog(title="Fixture Exporter for Maya", message="Export complete!", button=["Yay!"])

def CombineAndReparent():
    newSelectionList = []
    selectionList = Cmds.ls(sl=True)
    for selection in selectionList:
        if Cmds.nodeType(selection) in ["transform"]:
            children = Cmds.listRelatives(selection, children=True)
            Cmds.select(cl=True)
            for child in children:
                Cmds.select(selection + "|" + child, add=True)
            if (len(children) == 1):
                Cmds.parent(w=True)
                Cmds.delete(selection)
            else:
                Cmds.polyUnite(ch=True, name=selection)
            Cmds.delete(ch=True)
            newName = selection;
            print newName
            if not newName.find("LOD") == -1:
                nameParts = newName.split('_', 1)
                newName = "%s_%s" % (nameParts[1], nameParts[0])
            Cmds.rename(newName)
            Cmds.polyQuad(a=30, kgb=True, ktb=True, khe=True, ws=True, ch=True)
            newSelectionList.extend(Cmds.ls(sl=True))

    for selection in newSelectionList:
        Cmds.select(selection, add=True)
        
    Cmds.group(name="Scene")
    Cmds.delete(ch=True)
    
def CreateNewUVSetAndCombine():
    newSelectionList = []
    selectionList = Cmds.ls(sl=True)
    Cmds.select(cl=True)
    for selection in selectionList:
        Cmds.select(selection, add=True)
        if not "CosmopolisUVSet" in Cmds.polyUVSet(selection, query=True, allUVSets=True):
            Cmds.polyUVSet(selection, rename=True, newUVSet='CosmopolisUVSet')
        Cmds.polyUVSet(selection, currentUVSet=True, uvSet='CosmopolisUVSet')
    Cmds.polyUnite(ch=True)
    Cmds.polyUVSet(currentUVSet=True, uvSet='CosmopolisUVSet')

def CreateLightmapUVSet():
    selectionList = Cmds.ls(sl=True)
    for selection in selectionList:
        if not "Lightmap" in Cmds.polyUVSet(selection, query=True, allUVSets=True):
            Cmds.polyAutoProjection(selection, lm=1, pb=False, ibd=True, cm=True, l=2, sc=2, o=1, p=6, uvSetName="Lightmap", ps=0.2, ws=True)
            Cmds.polyUVSet(selection, luv=True)
        else:
            print "Lightmap UV set already exists"
    
    Cmds.confirmDialog(title="SceneExporter", message="Lightmap UV set generation complete!", button=["Yay!"])

'''
To rename the shading groups with the same name as that of the texture file.

import maya.cmds as Cmds;

counter = 0;
shadingGroups = Cmds.lsThroughFilter('DefaultShadingGroupsFilter9', na=True)
for shadingGroup in shadingGroups:
    surfaceShader = Cmds.listConnections(shadingGroup + '.surfaceShader', source=True, destination=False)
    if surfaceShader != None:
        colorNode = Cmds.listConnections(surfaceShader[0] + '.color', source=True, destination=False)
        if colorNode != None:
            textureFilename = Cmds.getAttr(colorNode[0] + '.fileTextureName').split('/')[-1].split('.')[0]
            if textureFilename != None:
                counter = counter + 1
                Cmds.rename(shadingGroup, textureFilename + 'XY' + str(counter) + 'ZW')
'''

'''
To create the new UV set

import maya.cmds as Cmds

sceneItems = Cmds.listRelatives('Scene', children=True)
for sceneItem in sceneItems:
    Cmds.polyUVSet(sceneItem, cr=True, uvSet='MapsUV')
    Cmds.polyUVSet(sceneItem, uvSet='MapsUV', currentUVSet=True)

hilite Building3 ;
selectMode 1 ;
select -r Building3.f[0:1176] ;
polyAutoProjection -lm 1 -pb 0 -ibd 1 -cm 0 -l 2 -sc 2 -o 0 -p 6 -ps 0.2 -ws 1 Building3.f[0:1176];
'''

'''
To select all items under the Scene node

import maya.cmds as Cmds

Cmds.select(cl=True)
sceneItems = Cmds.listRelatives('Scene', children=True)
for sceneItem in sceneItems:
    Cmds.select(sceneItem, add=True)
'''

'''
To get the positions of items

import maya.cmds as Cmds

Cmds.select(cl=True)
sceneItems = Cmds.listRelatives('Scene', children=True)
for sceneItem in sceneItems:
    position = Cmds.xform(sceneItem, q=True, rp=True)
'''

'''
To get selected items

import maya.cmds as Cmds;

selectedItems = Cmds.ls(sl=True)
'''

'''
To work on a node's shaderEngines

import maya.cmds as Cmds

connections = Cmds.listConnections("Car_LadaShape4", d=False, s=True, t="shadingEngine")
for c in range(0, len(connections)):
    print c, connections[c], Cmds.nodeType(connections[c])
    shaderConnections = Cmds.listConnections(connections[c], d=False, s=True)
    for sc in range(0, len(shaderConnections)):
        #print '', sc, shaderConnections[sc], Cmds.nodeType(shaderConnections[sc])
        if Cmds.nodeType(shaderConnections[sc]) in ["phong"]:
            #print Cmds.listAttr(shaderConnections[sc])
            print Cmds.getAttr(shaderConnections[sc] + ".color")
            print Cmds.getAttr(shaderConC:\Documents and Settings\Cosmopolis\My Documents\maya\2009\scripts
            nections[sc] + ".diffuse")
            
'''

'''
To use this in the shelf

import SceneExporter as Se
reload(Se)
Se.Run()
'''

'''
To use CombineAndReparent() in the shelf

import SceneExporter as Se
reload(Se)
Se.CombineAndReparent()
'''

'''
addAttr -ln "PhysicsShape"  -at "enum" -en "Mesh:Hull:"  |Scene|Straight_City_Street:Straight_City_Street;
setAttr -e-keyable true |Scene|Straight_City_Street:Straight_City_Street.PhysicsShape;
'''

'''
import maya.cmds as Cmds

Cmds.select(cl=True)
sceneItems = Cmds.listRelatives('Scene', children=True)
for sceneItem in sceneItems:
    print sceneItem
'''

'''
polyAutoProjection -lm 1 -pb 0 -ibd 1 -cm 1 -l 2 -sc 2 -o 1 -p 6 -uvSetName Lightmap -ps 0.2 -ws 1 Straight_City_Street4:Straight_City_Street.f[0:11];
// polyAutoProj1 // 
polyUVSet -luv Straight_City_Street4:Straight_City_Street.f[0:11];
// Lightmap //
// Cmd: convertLightmap  -camera persp -sh -bo tmpTextureBakeSet Straight_City_Street5:lambert2SG |Scene|Straight_City_Street5:Straight_City_Street|Straight_City_Street5:Straight_City_StreetShape // 
'''