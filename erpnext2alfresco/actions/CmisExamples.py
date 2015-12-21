'''
Created on Jan 20, 2012

@author: jpotts
'''
import time, datetime
import cmislibalf
from cmislib.model import CmisClient

# CMIS repository's service URL
#REPOSITORY_URL = 'http://cmis.alfresco.com/s/cmis' # Alfresco demo
#REPOSITORY_URL = 'http://localhost:8081/chemistry/atom' # Apache Chemistry
REPOSITORY_URL = 'http://localhost:8080/alfresco/cmisatom'  # Alfresco 4.0
#REPOSITORY_URL = 'http://localhost:8080/alfresco/s/api/cmis'  # Alfresco

# CMIS repository credentials
USERNAME = 'admin' # Alfresco
PASSWORD = 'admin' # Alfresco

# Folder in the root where test docs should be created
FOLDER_NAME = 'cmislib'

TYPE = 'whitepaper'
NAME = 'sample'
RESULT_SEP = "======================"

class CmisExamples():

    def __init__(self):
        self.setup()
        
    def setup(self):
        self._client = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
        self._repo = self._client.defaultRepository

    def dataCreator(self):
        doc = self.createTestDoc()
        
        print "Created: %s" % doc.id
        print "Content Length: %s" % doc.properties['cmis:contentStreamLength']

    def createTestDoc(self):        
        folder = self._repo.getObjectByPath("/" + FOLDER_NAME)
        fileName = NAME + " (" + str(time.time()) + ")"

        properties = {}
        #properties['cmis:objectTypeId'] = "D:sc:whitepaper"
        properties['cmis:name'] = fileName

        docText = "This is a sample " + TYPE + " document called " + NAME

        doc = folder.createDocumentFromString(fileName, properties, contentString=docText, contentType="text/plain")
        
        # Add two custom aspects and set aspect-related properties
        #doc.addAspect('P:sc:webable')
        #doc.addAspect('P:sc:productRelated')
        #props = {}
        #props['sc:isActive'] = True
        #props['sc:published'] = datetime.datetime(2007, 4, 1)
        #props['sc:product'] = 'SomePortal'
        #props['sc:version'] = '1.1'
        #doc.updateProperties(props)

        #print "isActive: %s" % doc.properties['sc:isActive']
        #print "published: %s" % doc.properties['sc:published']
        #print "product: %s" % doc.properties['sc:product']
        #print "version: %s" % doc.properties['sc:version']

        return doc

    def dataQueries(self):
        print RESULT_SEP
        print "Finding content of type: sc:doc"
        queryString = "select * from sc:doc"
        self.dumpQueryResults(self.getQueryResults(queryString))
                
        print RESULT_SEP
        print "Find content in the test folder with text like 'sample'"
        queryString = "select * from cmis:document where contains('sample') and in_folder('" + self.getFolderId(FOLDER_NAME) + "')"
        print "query string:%s" % queryString
        self.dumpQueryResults(self.getQueryResults(queryString))
                        
        print RESULT_SEP
        print "Find active content"
        queryString = "select d.*, w.* from cmis:document as d join sc:webable as w on d.cmis:objectId = w.cmis:objectId where w.sc:isActive = True"
        self.dumpQueryResults(self.getQueryResults(queryString))
        
        print RESULT_SEP
        print "Find active content with a product equal to 'SomePortal'"
        # There is no way to do a join across two aspects and subqueries aren't supported so we
        # are forced to execute two queries.
        queryString1 = """select d.cmis:objectId
                          from cmis:document as d
                          join sc:productRelated as p on d.cmis:objectId = p.cmis:objectId
                          where p.sc:product = 'SomePortal'"""
        queryString2 = """select d.cmis:objectId, d.cmis:name, d.cmis:creationDate
                          from cmis:document as d
                          join sc:webable as w on d.cmis:objectId = w.cmis:objectId
                          where w.sc:isActive = True"""
        self.dumpQueryResults(self.getSubQueryResults(queryString1, queryString2))

        print RESULT_SEP
        print "Find content of type sc:whitepaper published between 1/1/2006 and 6/1/2007"    
        queryString = """select d.cmis:objectId, d.cmis:name, d.cmis:creationDate, w.sc:published
                         from sc:whitepaper as d
                         join sc:webable as w on d.cmis:objectId = w.cmis:objectId
                         where w.sc:published > TIMESTAMP '2006-01-01T00:00:00.000-05:00'
                         and w.sc:published < TIMESTAMP '2007-06-02T00:00:00.000-05:00'"""
        self.dumpQueryResults(self.getQueryResults(queryString))

    def dataRelater(self):
        doc1 = self.createTestDoc()
        doc2 = self.createTestDoc()
        doc3 = self.createTestDoc()
                
        self._repo.createRelationship(doc1, doc2, 'R:sc:relatedDocuments')
        self._repo.createRelationship(doc1, doc3, 'R:sc:relatedDocuments')
        self.dumpRelationships(doc1)
        
    def dumpRelationships(self, sourceDoc):
        relList = sourceDoc.getRelationships()
        
        print "Associations of %s (%s)" % (sourceDoc.name, sourceDoc.id)
        for rel in relList:
            print "    %s" % rel.getTarget().id
   
    def dataCleaner(self):
        queryString = "select * from sc:doc where in_folder('" + self.getFolderId(FOLDER_NAME) + "')"
        resultSet = self._repo.query(queryString)

        # if we found some rows, create an array of DeleteCML objects
        if (len(resultSet) >= 0):        
            print "Found %s objects to delete." % len(resultSet)

        for res in resultSet:
            objectId = res.id
            res.reload()
            res.delete()
            print "Deleted: %s" % objectId

        print "Done!"

    def dumpQueryResults(self, resultSet):
        iCount = 0
        for res in resultSet:
            print "----------------------\r\nResult %s:" % iCount
            print "id:%s" % res.id
            print "name:%s" % res.name
            print "created:%s" % res.properties['cmis:creationDate']
            iCount += 1
    
    def getQueryResults(self, queryString):
        return self._repo.query(queryString)
    
    def getFolderId(self, folderName):
        queryString = "select cmis:objectId from cmis:folder where cmis:name = '" + folderName + "'"
        resultSet = self._repo.query(queryString)
        return resultSet[0].id
    
    def getSubQueryResults(self, queryString1, queryString2):
        rs = self._repo.query(queryString1)
        objIdList = []        

        for res in rs:
            objectId = res.id
            objIdList.append("'" + objectId + "'")
        
        if (len(objIdList) == 0):
            return []
        
        queryString = queryString2 + " AND d.cmis:objectId IN " + '(' + ','.join(objIdList) + ')'
        return self.getQueryResults(queryString)
        
if __name__ == "__main__":
    ex = CmisExamples()
    ex.dataCreator()   
    ex.dataQueries()
    ex.dataRelater()
    #ex.dataCleaner()