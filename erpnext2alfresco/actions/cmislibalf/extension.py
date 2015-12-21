#
#      Licensed to the Apache Software Foundation (ASF) under one
#      or more contributor license agreements.  See the NOTICE file
#      distributed with this work for additional information
#      regarding copyright ownership.  The ASF licenses this file
#      to you under the Apache License, Version 2.0 (the
#      "License"); you may not use this file except in compliance
#      with the License.  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing,
#      software distributed under the License is distributed on an
#      "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#      KIND, either express or implied.  See the License for the
#      specific language governing permissions and limitations
#      under the License.
#
from ..cmislib import model
from ..cmislib.exceptions import InvalidArgumentException
import datetime

ALFRESCO_NS = 'http://www.alfresco.org'
ALFRESCO_NSALIAS = 'alf'
ALFRESCO_NSALIAS_DECL = 'xmlns:' + ALFRESCO_NSALIAS
ALFRESCO_NSPREFIX = ALFRESCO_NSALIAS + ':'

LOCALNAME_ASPECTS = 'aspects'
LOCALNAME_PROPERTIES = 'properties'
LOCALNAME_APPLIED_ASPECTS = 'appliedAspects'
LOCALNAME_SET_ASPECTS = 'setAspects'
LOCALNAME_ASPECTS_TO_ADD = 'aspectsToAdd'
LOCALNAME_ASPECTS_TO_REMOVE = 'aspectsToRemove'

TAGNAME_ALFRESCO_PROPERTIES = ALFRESCO_NSPREFIX + LOCALNAME_PROPERTIES
TAGNAME_SET_ASPECTS = ALFRESCO_NSPREFIX + LOCALNAME_SET_ASPECTS
TAGNAME_ASPECTS_TO_ADD = ALFRESCO_NSPREFIX + LOCALNAME_ASPECTS_TO_ADD
TAGNAME_ASPECTS_TO_REMOVE = ALFRESCO_NSPREFIX + LOCALNAME_ASPECTS_TO_REMOVE

OBJECT_TYPE_ID = 'cmis:objectTypeId'
CHANGE_TOKEN = 'cmis:changeToken'

def addSetAspectsToXMLDocument(xmldoc):
    entryElements = xmldoc.getElementsByTagNameNS(model.ATOM_NS, 'entry')
    entryElements[0].setAttribute(ALFRESCO_NSALIAS_DECL, ALFRESCO_NS)
    
    propertiesElements = xmldoc.getElementsByTagNameNS(model.CMIS_NS, LOCALNAME_PROPERTIES)
    if len(propertiesElements) == 0:
        objectElement = xmldoc.getElementsByTagNameNS(model.CMISRA_NS, 'object')
        propertiesElement = xmldoc.createElementNS(model.CMIS_NS, 'cmis:properties')
        objectElement[0].appendChild(propertiesElement)
    else:
        propertiesElement = propertiesElements[0]
    
    aspectsElement = xmldoc.createElementNS(ALFRESCO_NS, TAGNAME_SET_ASPECTS)
    propertiesElement.appendChild(aspectsElement)
    
    return aspectsElement

def addPropertiesToXMLElement(xmldoc, element, properties):
    for propName, propValue in properties.items():
        """
        the name of the element here is significant: it includes the
        data type. I should be able to figure out the right type based
        on the actual type of the object passed in.
    
        I could do a lookup to the type definition, but that doesn't
        seem worth the performance hit
        """
        propType = type(propValue)
        isList = False
        if (propType == list):
            propType = type(propValue[0])
            isList = True
    
        if (propType == model.CmisId):
            propElementName = 'cmis:propertyId'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(val)
            else:
                propValueStrList = [propValue]
        elif (propType == str):
            propElementName = 'cmis:propertyString'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(val)
            else:
                propValueStrList = [propValue]
        elif (propType == datetime.datetime):
            propElementName = 'cmis:propertyDateTime'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(val.isoformat())
            else:
                propValueStrList = [propValue.isoformat()]
        elif (propType == bool):
            propElementName = 'cmis:propertyBoolean'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(unicode(val).lower())
            else:
                propValueStrList = [unicode(propValue).lower()]
        elif (propType == int):
            propElementName = 'cmis:propertyInteger'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(unicode(val))
            else:
                propValueStrList = [unicode(propValue)]
        elif (propType == float):
            propElementName = 'cmis:propertyDecimal'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(unicode(val))
            else:
                propValueStrList = [unicode(propValue)]
        else:
            propElementName = 'cmis:propertyString'
            if isList:
                propValueStrList = []
                for val in propValue:
                    propValueStrList.append(unicode(val))
            else:
                propValueStrList = [unicode(propValue)]
    
        propElement = xmldoc.createElementNS(model.CMIS_NS, propElementName)
        propElement.setAttribute('propertyDefinitionId', propName)
        for val in propValueStrList:
            valElement = xmldoc.createElementNS(model.CMIS_NS, 'cmis:value')
            valText = xmldoc.createTextNode(val)
            valElement.appendChild(valText)
            propElement.appendChild(valElement)
        element.appendChild(propElement)

def initData(self):
    model.CmisObject._initData(self)
    self._aspects = {}
    self._alfproperties = {}

def findAlfrescoExtensions(self):
    if not hasattr(self, '_aspects'):
        self._aspects = {}
    if self._aspects == {}:
        if self.xmlDoc == None:
            self.reload()
        appliedAspects = self.xmlDoc.getElementsByTagNameNS(ALFRESCO_NS, LOCALNAME_APPLIED_ASPECTS)
        for node in appliedAspects:
            aspectType = self._repository.getTypeDefinition(node.childNodes[0].data)
            self._aspects[node.childNodes[0].data] = aspectType

def hasAspect(self, arg):
    result = False
    if arg is not None:
        self._findAlfrescoExtensions()
        if isinstance(arg, model.ObjectType):
            result = arg.getTypeId() in self._aspects
        else:
            result = arg in self._aspects
    return result

def getAspects(self):
    self._findAlfrescoExtensions()
    return self._aspects.values()

def findAspect(self, propertyId):
    self._findAlfrescoExtensions()
    if (propertyId is not None) and (len(self._aspects) > 0):
        for id, aspect in self._aspects.iteritems():
            props = aspect.getProperties()
            if propertyId in props:
                return aspect
    return None

def updateAspects(self, addAspects=None, removeAspects=None):
    if addAspects or removeAspects:
        selfUrl = self._getSelfLink()
        xmlEntryDoc = getEntryXmlDoc(self._repository)
        # Patch xmlEntryDoc
        setAspectsElement = addSetAspectsToXMLDocument(xmlEntryDoc)
        
        if addAspects:
            addAspectElement = xmlEntryDoc.createElementNS(ALFRESCO_NS, TAGNAME_ASPECTS_TO_ADD)
            valText = xmlEntryDoc.createTextNode(addAspects)
            addAspectElement.appendChild(valText)
            setAspectsElement.appendChild(addAspectElement)
        
        if removeAspects:
            removeAspectElement = xmlEntryDoc.createElementNS(ALFRESCO_NS, TAGNAME_ASPECTS_TO_REMOVE)
            valText = xmlEntryDoc.createTextNode(removeAspects)
            removeAspectElement.appendChild(valText)
            setAspectsElement.appendChild(removeAspectElement)
        
        updatedXmlDoc = self._cmisClient.put(selfUrl.encode('utf-8'),
                                             xmlEntryDoc.toxml(encoding='utf-8'),
                                             model.ATOM_XML_TYPE)
    
        self.xmlDoc = updatedXmlDoc
        self._initData()

def getProperties(self):
    result = model.CmisObject.getProperties(self)
    if not hasattr(self, '_alfproperties'):
        self._alfproperties = {}
    if self._alfproperties == {}:
        alfpropertiesElements = self.xmlDoc.getElementsByTagNameNS(ALFRESCO_NS, LOCALNAME_PROPERTIES)
        if len(alfpropertiesElements) > 0:
            for alfpropertiesElement in alfpropertiesElements:
                for node in [e for e in alfpropertiesElement.childNodes if e.nodeType == e.ELEMENT_NODE and e.namespaceURI == model.CMIS_NS]:
                    #propertyId, propertyString, propertyDateTime
                    #propertyType = cpattern.search(node.localName).groups()[0]
                    propertyName = node.attributes['propertyDefinitionId'].value
                    if node.childNodes and \
                       node.getElementsByTagNameNS(model.CMIS_NS, 'value')[0] and \
                       node.getElementsByTagNameNS(model.CMIS_NS, 'value')[0].childNodes:
                        valNodeList = node.getElementsByTagNameNS(model.CMIS_NS, 'value')
                        if (len(valNodeList) == 1):
                            propertyValue = model.parsePropValue(valNodeList[0].
                                                           childNodes[0].data,
                                                           node.localName)
                        else:
                            propertyValue = []
                            for valNode in valNodeList:
                                propertyValue.append(model.parsePropValue(valNode.
                                                           childNodes[0].data,
                                                           node.localName))
                    else:
                        propertyValue = None
                    self._alfproperties[propertyName] = propertyValue
    result.update(self._alfproperties)
    return result

def updateProperties(self, properties):
    selfUrl = self._getSelfLink()
    cmisproperties = {}
    alfproperties = {}

    # if we have a change token, we must pass it back, per the spec
    args = {}
    if (self.properties.has_key(CHANGE_TOKEN) and
        self.properties[CHANGE_TOKEN] != None):
        self.logger.debug('Change token present, adding it to args')
        args = {"changeToken": self.properties[CHANGE_TOKEN]}

    objectTypeId = properties.get(OBJECT_TYPE_ID)
    if (objectTypeId is None):
        objectTypeId = self.properties.get(OBJECT_TYPE_ID)
    objectType = self._repository.getTypeDefinition(objectTypeId)
    objectTypePropsDef = objectType.getProperties()
    
    for propertyName, propertyValue in properties.items():
        if (propertyName == OBJECT_TYPE_ID) or (propertyName in objectTypePropsDef.keys()):
            cmisproperties[propertyName] = propertyValue
        else:
            if self.findAspect(propertyName) is None:
                raise InvalidArgumentException
            else:
                alfproperties[propertyName] = propertyValue
    
    xmlEntryDoc = getEntryXmlDoc(self._repository, properties=cmisproperties)
    
    # Patch xmlEntryDoc
    # add alfresco properties
    if len(alfproperties) > 0:
        aspectsElement = addSetAspectsToXMLDocument(xmlEntryDoc)
        
        alfpropertiesElement = xmlEntryDoc.createElementNS(ALFRESCO_NS, TAGNAME_ALFRESCO_PROPERTIES)
        aspectsElement.appendChild(alfpropertiesElement)
        # Like regular properties
        addPropertiesToXMLElement(xmlEntryDoc, alfpropertiesElement, alfproperties)
    
    updatedXmlDoc = self._cmisClient.put(selfUrl.encode('utf-8'),
                                         xmlEntryDoc.toxml(encoding='utf-8'),
                                         model.ATOM_XML_TYPE,
                                         **args)
    self.xmlDoc = updatedXmlDoc
    self._initData()
    return self

def addAspect(self, arg):
    if arg is not None:
        aspect_id = arg
        if isinstance(arg, model.ObjectType):
            aspect_id = arg.getTypeId()
        if self._repository.getTypeDefinition(aspect_id) is None:
            raise InvalidArgumentException
        self._updateAspects(addAspects=aspect_id)

def removeAspect(self, arg):
    if arg is not None:
        aspect_id = arg
        if isinstance(arg, model.ObjectType):
            aspect_id = arg.getTypeId()
        if self._repository.getTypeDefinition(aspect_id) is None:
            raise InvalidArgumentException
        self._updateAspects(removeAspects=aspect_id)

def getEntryXmlDoc(repo=None, objectTypeId=None, properties=None, contentFile=None,
                    contentType=None, contentEncoding=None):
    return model.getEntryXmlDoc(repo, objectTypeId, properties, contentFile, contentType, contentEncoding)