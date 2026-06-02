from django.shortcuts import render
from django.shortcuts import redirect

from .forms import IncidentForm
from .forms import HazardImageFormSet

from .models import Incident


def dashboard(request):

    incidents = Incident.objects.all()

    return render(
        request,
        'dashboard.html',
        {
            'incidents': incidents
        }
    )


def create_incident(request):

    if request.method == 'POST':

        form = IncidentForm(request.POST)

        if form.is_valid():

            incident = form.save()

            formset = HazardImageFormSet(
                request.POST,
                request.FILES,
                instance=incident
            )

            if formset.is_valid():
                formset.save()

            return redirect('dashboard')

    else:

        form = IncidentForm()
        formset = HazardImageFormSet()

    return render(
        request,
        'incident/create.html',
        {
            'form': form,
            'formset': formset
        }
    )