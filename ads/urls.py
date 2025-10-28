from django.urls import path
from . import views

app_name = "ads"

urlpatterns = [
    path("", views.ad_dashboard, name="dashboard"),  # Dashboard
    path("create/", views.create_ad_campaign, name="create_ad_campaign"),  # Step 1
    path("save/", views.create_ad, name="create_ad"),  # Step 2 - final save after UTR
    path("thank-you/<int:ad_id>/", views.ad_thank_you, name="ad_thank_you"),  # Thank You page
    path("dashboard/", views.ads_dashboard, name="ads_dashboard"),
]
