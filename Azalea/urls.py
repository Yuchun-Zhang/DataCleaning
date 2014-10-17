from django.conf.urls import patterns, include, url

#Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Azalea.views.home', name='home'),
    # url(r'^Azalea/', include('Azalea.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'Azalea.views.DBName', name='DBName'),
    url(r'^TableName/$', 'Azalea.views.TableName', name='TableName'),
    url(r'^ShowTable/$', 'Azalea.views.ShowTable', name='ShowTable'),   
    url(r'^Relation/$', 'Azalea.views.Relation', name='Relation'),
    url(r'^ProcessPropVar/$', 'Process.views.PropVar', name='ProcessPropVar'),
    url(r'^ProcessMatrixSolve/$', 'Process.MatrixSolve.MatrixSolve', name='ProcessMatrixSolve'),   
    url(r'^ProcessShowProb/$', 'Process.ShowProb.ShowProb', name='ProcessShowProb'),   
    url(r'^ProcessAutoRepair/$', 'Process.AutoRepair.AutoRepair', name='ProcessAutoRepair'),   
    url(r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/DevProjects/Azalea/img'}), 
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/DevProjects/Azalea/css'}), 
)
