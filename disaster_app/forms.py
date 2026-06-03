from django import forms
from django.forms import inlineformset_factory

from .models import Incident
from .models import HazardImage


class IncidentForm(forms.ModelForm):

    class Meta:
        model = Incident
        fields = (
    "title",
    "description",
    "status",
)


HazardImageFormSet = inlineformset_factory(
    Incident,
    HazardImage,
    fields=("image", "caption"),
    extra=1,
    can_delete=True
)