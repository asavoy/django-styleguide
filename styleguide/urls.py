from django.conf.urls.defaults import patterns, url
from styleguide.views import IndexView, SectionView


urlpatterns = patterns('',

   url(r'^$',
       IndexView.as_view(),
       name=r'styleguide_index'),

   url(r'^section/(?P<position>\d+)/$',
       SectionView.as_view(),
       name=r'styleguide_section'),

)






