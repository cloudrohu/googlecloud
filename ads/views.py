from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import IntegrityError
from .forms import AdCampaignForm
from .models import AdCampaign
import json


# =====================================
# 1️⃣ DASHBOARD — Add & View Campaigns
# =====================================


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import AdCampaign


@login_required
def ads_dashboard(request):
    """
    User Ads Dashboard:
    - Shows total ad campaigns, total spent, last purchase date
    - Displays full purchase history table
    """
    campaigns = AdCampaign.objects.filter(user=request.user).order_by("-created_at")

    # Auto-expire check for all campaigns
    for ad in campaigns:
        ad.check_and_update_status()

    # Calculate totals
    total_ads = campaigns.count()
    total_spent = campaigns.filter(status__in=["PAID", "UNDER_REVIEW"]).aggregate(
        total=Sum("daily_budget")
    )["total"] or 0

    # Total spent with GST
    total_with_gst = sum(ad.total_with_gst for ad in campaigns if ad.status in ["PAID", "UNDER_REVIEW"])

    last_purchase = campaigns.first().created_at if total_ads > 0 else None

    context = {
        "ads": campaigns,
        "total_ads": total_ads,
        "total_spent": total_with_gst,
        "last_purchase": last_purchase,
    }

    return render(request, "ads/dashboard.html", context)





@login_required
def ad_dashboard(request):
    """User dashboard for adding and viewing ad campaigns"""
    campaigns = AdCampaign.objects.filter(user=request.user).order_by("-id")

    if request.method == "POST":
        form = AdCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            return redirect("ads:dashboard")
    else:
        form = AdCampaignForm()

    return render(request, "ads/index.html", {
        "form": form,
        "campaigns": campaigns,
    })


# =====================================
# 2️⃣ CREATE (Step 1) — Ad Campaign Calculation (Before UTR)
# =====================================
@csrf_exempt
@login_required
def create_ad_campaign(request):
    """
    Step 1: Create temporary ad and return total (used for front-end display)
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            domain = data.get("domain_name")
            budget = data.get("daily_budget")
            duration = int(data.get("duration"))

            campaign = AdCampaign.objects.create(
                user=request.user,
                domain_name=domain,
                daily_budget=budget,
                duration=duration
            )

            return JsonResponse({
                "success": True,
                "message": "Ad Campaign created successfully",
                "total": float(campaign.total_with_gst)
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=405)


# =====================================
# 3️⃣ CREATE (Step 2) — After UTR Confirmation (Final Save)
# =====================================


@csrf_exempt
def create_ad(request):
    """
    Step 2: Save confirmed Ad after UTR verification
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user if request.user.is_authenticated else None

            domain = data.get("domain_name")
            budget = data.get("daily_budget")
            duration = data.get("duration")
            utr_id = data.get("utr_id")

            # ✅ Validation
            if not utr_id or len(utr_id) != 12:
                return JsonResponse({
                    "success": False,
                    "error": "Invalid UTR ID (must be 12 digits)"
                }, status=400)

            # ✅ Check for duplicate UTR
            if AdCampaign.objects.filter(utr_id=utr_id).exists():
                return JsonResponse({
                    "success": False,
                    "error": "❌ This UTR ID has already been used. Please verify your payment ID."
                }, status=400)

            # ✅ Create new Ad Campaign
            ad = AdCampaign.objects.create(
                user=user,
                domain_name=domain,
                daily_budget=budget,
                duration=duration,
                utr_id=utr_id,
                status="UNDER_REVIEW"
            )

            return JsonResponse({
                "success": True,
                "redirect_url": f"/ads/thank-you/{ad.id}/"
            })

        except IntegrityError:
            return JsonResponse({
                "success": False,
                "error": "This UTR ID is already linked with another transaction."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, status=400)

    return JsonResponse({"success": False, "error": "Invalid Request"}, status=405)


# =====================================
# 4️⃣ THANK YOU PAGE
# =====================================
def ad_thank_you(request, ad_id):
    """Render Ads Thank You Page"""
    ad = get_object_or_404(AdCampaign, id=ad_id)
    return render(request, "ads/thank_you.html", {"ad": ad})
