from __future__ import unicode_literals
import time, datetime, os, pdfkit
import cmislibalf
from cmislib.model import CmisClient
import frappe
from frappe import msgprint
from frappe.utils.pdf import get_pdf
from frappe.utils import cint, strip_html, scrub_urls
from frappe import _


#REPOSITORY_URL = 'http://localhost:8080/alfresco/cmisatom'  # Alfresco 4.0
#USERNAME = 'admin' # Alfresco
#PASSWORD = 'admin' # Alfresco

FOLDER_NAME = 'Test/cmislib'
NAME = 'cmislib_file'
TYPE = 'TestType'
standard_format = "templates/print_formats/standard.html"

def submit_document(doc, method=None):
	
	repository_disabled = frappe.db.get_single_value("Repository", "disabled")
	if repository_disabled == 0:
		mapping_path = frappe.db.get_value("Mapping", {"doc_type": doc.doctype}, "doc_path")
		
		if mapping_path is not None:
			mapping_disabled = frappe.db.get_value("Mapping", {"doc_type": doc.doctype}, "doc_type_disabled")
			if mapping_disabled == 0:
				try:
					repositoryURL = frappe.db.get_single_value("Repository", "url")
					userName = frappe.db.get_single_value("Repository", "userid")
					userPass = frappe.db.get_single_value("Repository", "password")
					#msgprint("RepURL ... "+repositoryURL+" "+userName+" "+userPass, [doc])
					client = CmisClient(repositoryURL, userName, userPass)
					repo = client.defaultRepository

					mapping_name = frappe.db.get_value("Mapping", {"doc_type": doc.doctype}, "name")
					mapping_type = frappe.db.get_value("Mapping", {"doc_type": doc.doctype}, "doc_type_alfresco")
					mapping_user = frappe.db.get_value("User Mapping", {"erpnext_user": frappe.session.user}, "alfresco_user", None, False, False)
					if mapping_user is None:
						mapping_user = "ERPNext2Alfresco"
					
					mapping_properties = frappe.db.get_values("Mapping Item",
									{"parent": mapping_name},
									["db_field", "alfresco_aspect", "alfresco_property"], as_dict=True)
					#for map_det in mapping_properties:
					#	print map_det
			
					docu = createDoc(doc, repo, mapping_path, mapping_type, mapping_properties)
				except Exception, e:
					#print e
					frappe.throw(_("<p>Cannot connect to Alfresco Repository</p><p><ul><li>Please check the Repository Settings</li><li>Disable the Repository</li><li>Disable the DocType Mapping</li></ul></p>"))
					#	msgprint("Document submitted ... ", [doc])
			else:
				#pass
				msgprint("Doctype disabled ... ", [doc])
		else:
			pass
	else:
		msgprint("Repository disabled ... ", [doc])

	#frappe.db.close()
	#msgprint("Document submitted ... ", [doc])

def cancel_document(doc, method=None):
	#msgprint("Document canceled ... ", [doc])
	pass

def delete_document(doc, method=None):
	#msgprint("Document deleted ... ", [doc])
	pass


def createDoc(document, repo, path, alfresco_type, mapping_properties):  

	
	html = frappe.get_print( document.doctype, document.name)
	fileName = "{name}.pdf".format(name=document.name.replace(" ", "-").replace("/", "-"))
	print fileName
	options = {}

	options.update({
		"print-media-type": None,
		"background": None,
		"images": None,
		'margin-top': '15mm',
		'margin-right': '15mm',
		'margin-bottom': '15mm',
		'margin-left': '15mm',
		'encoding': "UTF-8",
		'no-outline': None
	})

	if not options.get("page-size"):
		options['page-size'] = frappe.db.get_single_value("Print Settings", "pdf_page_size") or "A4"

	html = scrub_urls(html)
	fname = os.path.join("/tmp", frappe.generate_hash() + ".pdf")
	pdfkit.from_string(html, fname, options=options or {})

	#with open(fname, "rb") as fileobj:
		#filedata = fileobj.read()
	fileobj = open(fname, "rb")
	
	folder = repo.getObjectByPath("/" + path)
	#fileName = document.name + ".pdf"
	properties = {}
	properties['cmis:objectTypeId'] = "D:"+alfresco_type
	properties['cmis:name'] = document.name
	
	#docu = folder.createDocument(fileName, properties, contentFile=fileobj, contentType="application/pdf")
	# Hier muss noch die Verarbeitung der Aspects hin
	props = {}
	dict = {}

	default_key = "default"
	#print mapping_properties
	for map_det in mapping_properties:
		if map_det.alfresco_aspect is None or len(map_det.alfresco_aspect.strip()) < 1:
			props[map_det.alfresco_property] = document.__dict__[map_det.db_field]
			#properties[map_det.alfresco_property] = document.__dict__[map_det.db_field]
			if default_key in dict:
				act_props = dict[default_key]
				act_props[map_det.alfresco_property] = document.__dict__[map_det.db_field]
			else:
				act_props = {}
				act_props[map_det.alfresco_property] = document.__dict__[map_det.db_field]
				dict[default_key] = act_props
		else:
			alf_aspect_key = map_det.alfresco_aspect
			if alf_aspect_key in dict:
				act_props = dict[alf_aspect_key]
				act_props[map_det.alfresco_property] = document.__dict__[map_det.db_field]
			else:
				act_props = {}
				act_props[map_det.alfresco_property] = document.__dict__[map_det.db_field]
				dict[alf_aspect_key] = act_props

	#print frappe.session.user.name
	
	for key in dict:
		if key is default_key:
			list = dict[key]
			for listkey in list:
				#print listkey + ' : '+ list[listkey]
				properties[listkey] = list[listkey]

	print fileobj
	print properties

	docu = folder.createDocument(fileName, properties, contentFile=fileobj, contentType="application/pdf")
	#print docu
	#docu.updateProperties(props)

	for key in dict:
		if key is not default_key:
			print key
			docu.addAspect('P:'+key)
			list = dict[key]
			asp_props = {}
			for listkey in list:
				print listkey + ' : '+ list[listkey]
				asp_props[listkey] = list[listkey]
			docu.updateProperties(asp_props)


	os.remove(fname)
	return docu




