from django.urls import path, include

from user.views import CreateUserView

app_name = "user"

urlpatterns = [
    path("register", CreateUserView.as_view(), name="create"),
]
