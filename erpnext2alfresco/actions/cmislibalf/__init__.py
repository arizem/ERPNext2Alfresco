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
from extension import *

# Types' hooks
model.Document._initData = initData
model.Document._findAlfrescoExtensions = findAlfrescoExtensions
model.Document.hasAspect = hasAspect
model.Document.getAspects = getAspects
model.Document.findAspect = findAspect
model.Document._updateAspects = updateAspects
model.Document.getProperties = getProperties
model.Document.properties = property(getProperties)
model.Document.updateProperties = updateProperties
model.Document.addAspect = addAspect
model.Document.removeAspect = removeAspect

model.Folder._initData = initData
model.Folder._findAlfrescoExtensions = findAlfrescoExtensions
model.Folder.hasAspect = hasAspect
model.Folder.getAspects = getAspects
model.Folder.findAspect = findAspect
model.Folder._updateAspects = updateAspects
model.Folder.getProperties = getProperties
model.Folder.properties = property(getProperties)
model.Folder.updateProperties = updateProperties
model.Folder.addAspect = addAspect
model.Folder.removeAspect = removeAspect
