from django import forms
from django.contrib.auth import get_user_model

from apps.rewards.models import NGO, RedeemedReward, Reward, RewardNotification

User = get_user_model()


class NGOForm(forms.ModelForm):
    class Meta:
        model = NGO
        fields = ["name", "description", "email", "website", "logo"]


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = [
            "ngo",
            "title",
            "description",
            "points_required",
            "reward_type",
            "is_active",
        ]


class RewardNotificationForm(forms.ModelForm):
    notify_all_users = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = RewardNotification
        fields = ["user", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.order_by("username")
        self.fields["user"].required = False

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        notify_all = cleaned_data.get("notify_all_users")
        if not user and not notify_all:
            raise forms.ValidationError("Select a user or choose notify all users.")
        return cleaned_data
