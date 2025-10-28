from django import forms
from .models import AdCampaign

class AdCampaignForm(forms.ModelForm):
    class Meta:
        model = AdCampaign
        fields = ["domain_name", "daily_budget", "duration"]
        widgets = {
            "domain_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your domain (e.g. example.com)"
            }),
            "daily_budget": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter daily budget (₹350 minimum)"
            }),
            "duration": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        budget = cleaned_data.get("daily_budget")
        duration = cleaned_data.get("duration")

        # 1️⃣ Minimum budget check
        if budget is not None and budget < 350:
            raise forms.ValidationError("❌ Minimum daily budget must be ₹350 or higher.")

        # 2️⃣ Logic for allowed durations
        if budget is not None:
            if budget <= 2500:
                allowed = [30]
                if duration not in allowed:
                    raise forms.ValidationError("For budgets up to ₹2500, only '1 Month' (30 Days) is allowed.")
            elif 2500 < budget <= 10000:
                allowed = [15, 30]
                if duration not in allowed:
                    raise forms.ValidationError("For budgets between ₹2501–₹10000, select '15 Days' or '1 Month'.")
            elif budget > 10000:
                allowed = [7, 15, 30]
                if duration not in allowed:
                    raise forms.ValidationError("Invalid duration for this budget range.")

        return cleaned_data
