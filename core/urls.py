from django.urls import path
from core import views

urlpatterns = [
    path("", views.landing, name="landing"),

    # auth
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # docs
    path("documents/", views.documents, name="documents"),
    path("documents/upload/", views.document_upload, name="document_upload"),
    path("documents/<int:pk>/", views.document_detail, name="document_detail"),
    path("documents/<int:pk>/delete/", views.document_delete, name="document_delete"),
    path("documents/reindex/", views.document_reindex, name="document_reindex"),

    # chat
    path("chat/", views.chat, name="chat"),

    # logs
    path("logs/", views.logs, name="logs"),
    path("logs/clear/", views.clear_logs, name="clear_logs"),
]
