from django.conf.urls import url, include

urlpatterns = [
    url(
        r'^',
        include('paiji2_social.urls'),
    ),
    url(
        r'^calendar',
        include('backbone_calendar.urls'),
    ),
]
