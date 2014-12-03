from django.conf.urls.defaults import *
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', views.index),
    (r'^averages.png$', views.average_score_plot),
    (r'^mutation_rate.png$', views.average_mrate_plot),
    (r'^gen-(?P<generation>\d+)/(?P<orgname>.*)-coin_graph\.jpg$', views.coin_graph),
    (r'^gen-(?P<generation>\d+)/?$', views.generation),
    (r'^gen-(?P<generation>\d+)/(?P<orgname>.*)\.jpg$', views.screenshot),
    (r'^gen-(?P<generation>\d+)/movie/(?P<orgname>.*)$', views.movie),
    (r'^gen-(?P<generation>\d+)/(?P<orgname>.*)$', views.organism),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
