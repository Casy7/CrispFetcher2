from django import urls
from .views import *
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

urlpatterns = [
    path("", CrispFetcher.as_view(), name="home"),
    path("upload_xmls/", AjaxGetXMLs.as_view(), name="item"),
    path("signin/", Login.as_view(), name="login"),
    path("signout/", Logout.as_view(), name="logout"),
    path("signup/", SignUp.as_view(), name="registration"),
    path("recent/", RecentMerges.as_view(), name="recent"),
    path("save_xmls/", AjaxSaveXMLs.as_view(), name="save_xmls"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
