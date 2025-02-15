"""wild_politics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('sentry-debug/', trigger_error),
                  path('', include('social_django.urls', namespace='social')),
                  path('accounts/', include('allauth.urls')),
                  path('summernote/', include('django_summernote.urls')),

                  url(r'', include('player.url')),
                  url(r'', include('player.urls.profile')),
                  url(r'', include('player.urls.skills')),
                  url(r'', include('player.urls.customization')),
                  url(r'', include('region.urls')),

                  url(r'', include('article.urls.article')),

                  url(r'', include('education.urls.education')),

                  url(r'', include('storage.urls.storage')),
                  url(r'', include('storage.urls.assets')),
                  url(r'', include('storage.urls.trading')),
                  url(r'', include('storage.urls.auctions')),
                  url(r'', include('storage.urls.vault')),

                  url(r'', include('factory.urls.factory')),

                  url(r'', include('party.urls.party')),
                  url(r'', include('party.urls.list')),
                  url(r'', include('party.urls.roles')),
                  url(r'', include('party.urls.staff')),

                  url(r'', include('state.urls.government')),
                  url(r'', include('gov.urls.government')),
                  url(r'', include('bill.urls.bills')),

                  url(r'', include('war.urls.war')),

                  url(r'', include('polls.urls')),
                  url(r'', include('chat.urls')),

                  url(r'', include('skill.urls')),

                  url(r'', include('event.urls')),

                  url('__debug__/', include(debug_toolbar.urls)),

                  # url(r'', include('article.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]