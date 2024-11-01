from django.urls import path, include

import users.urls


urlpatterns = [
    path('v1/', include(users.urls)),

]
