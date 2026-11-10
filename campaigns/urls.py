from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path("", views.dashboard, name="dashboard"),
    path("dashboard/live-data/", views.dashboard_live_data, name="dashboard_live_data"),


    # Campaign Management
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/create/", views.campaign_create, name="campaign_create"),
    path("campaigns/edit/<int:pk>/", views.campaign_edit, name="campaign_edit"),
    path("campaigns/delete/<int:pk>/", views.campaign_delete, name="campaign_delete"),
    path("campaigns/<int:pk>/send/", views.campaign_send, name="campaign_send"),

    # Contact Management
    path("contacts/", views.contact_list, name="contact_list"),
    path("contacts/import/", views.import_contacts, name="import_contacts"),
    path("contacts/add/", views.contact_create, name="contact_create"),
    path("contacts/edit/<int:pk>/", views.contact_edit, name="contact_edit"),
    path("contacts/delete/<int:pk>/", views.contact_delete, name="contact_delete"),
    path("contacts/bulk-delete/", views.contact_bulk_delete, name="contact_bulk_delete"),

    # Contact Group Management
    path("groups/", views.group_list, name="group_list"),
    path("groups/add/", views.group_create, name="group_create"),
    path("groups/edit/<int:pk>/", views.group_edit, name="group_edit"),
    path("groups/delete/<int:pk>/", views.group_delete, name="group_delete"),

    path("email-logs/", views.email_logs, name="email_logs"),

    # Email Template Management
    path("templates/", views.template_list, name="template_list"),
    path("templates/add/", views.template_create, name="template_create"),
    path("templates/edit/<int:pk>/", views.template_edit, name="template_edit"),
    path("templates/delete/<int:pk>/", views.template_delete, name="template_delete"),

    path("template-details/<int:pk>/",views.get_template_details,name="get_template_details"),
    path("workflows/", views.workflow_list, name="workflow_list"),
    path("workflows/create/", views.workflow_create, name="workflow_create"),
    path("workflows/<int:pk>/edit/",views.workflow_edit,name="workflow_edit"),
    path("workflows/<int:pk>/delete/",views.workflow_delete,name="workflow_delete"),
    path("workflows/<int:pk>/toggle/",views.workflow_toggle,name="workflow_toggle"),
    path("email-logs/clear/", views.clear_all_logs, name="clear_all_logs"),
]