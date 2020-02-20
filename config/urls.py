from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from . import views

urlpatterns = [
    path("", views.HomeView, name="home"),
    path("analytics",views.AnalyticsView, name="analytics"),
    path("index/", views.index, name="index"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    path(
        "golden/", views.golden, name="golden"
    ),
    path("genome_browser/", views.genome_browser, name="genome_browser"),
    path(
        "tutorial/", TemplateView.as_view(template_name="pages/tutorial.html"), name="tutorial"
    ),
    path("unauthorized", views.render_403, name="unauthorized"),
    path(
        "tech_corner/", TemplateView.as_view(template_name="pages/tech_corner.html"), name="tech_corner"
    ),
    path(
        "founders/", TemplateView.as_view(template_name="pages/founder.html"), name="founders"
    ),
    path(
        "statistics/", TemplateView.as_view(template_name="pages/statistics.html"), name="statistics"
    ),
    path(
        "ressources/", TemplateView.as_view(template_name="pages/ressources.html"), name="ressources"
    ),
    path(
        "download/", TemplateView.as_view(template_name="pages/download.html"), name="download"
    ),
    path(
        "citing/", TemplateView.as_view(template_name="pages/citing.html"), name="citing"
    ),
    path(
        "help/", TemplateView.as_view(template_name="pages/help.html"), name="help"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("sdap.users.urls", namespace="users")),
    path("groups/", include("sdap.groups.urls", namespace="groups")),
    path("files/", include("sdap.files.urls", namespace="files")),
    path("tools/", include("sdap.tools.urls", namespace="tools")),
    path("jobs/", include("sdap.jobs.urls", namespace="jobs")),
    path("studies/", include("sdap.studies.urls", namespace="studies")),
    
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
