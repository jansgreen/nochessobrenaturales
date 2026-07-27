from .models import DonationSettings


def get_donation_url():
    return (
        DonationSettings.objects.filter(pk=1)
        .values_list("paypal_url", flat=True)
        .first()
        or ""
    )

