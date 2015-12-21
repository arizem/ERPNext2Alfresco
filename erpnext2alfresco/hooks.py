# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "erpnext2alfresco"
app_title = "ERPNext2Alfresco"
app_publisher = "Arizem"
app_description = "Export ERPNext Documents to Alfresco automatically"
app_icon = "icon-archive"
app_color = "#00BCDE"
app_email = "i.o@arizem.de"
app_version = "0.1.0"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext2alfresco/css/erpnext2alfresco.css"
# app_include_js = "/assets/erpnext2alfresco/js/erpnext2alfresco.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext2alfresco/css/erpnext2alfresco.css"
# web_include_js = "/assets/erpnext2alfresco/js/erpnext2alfresco.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "erpnext2alfresco.install.before_install"
# after_install = "erpnext2alfresco.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext2alfresco.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
 	"*": {
		"on_submit": "erpnext2alfresco.actions.submit_document",
		"on_cancel": "erpnext2alfresco.actions.cancel_document"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext2alfresco.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext2alfresco.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext2alfresco.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext2alfresco.tasks.weekly"
# 	]
# 	"monthly": [
# 		"erpnext2alfresco.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "erpnext2alfresco.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext2alfresco.event.get_events"
# }

