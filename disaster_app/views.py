from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db import connection

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


# ============================================================================
# HEALTH CHECK ENDPOINT - Production Monitoring & Cloud Deployment
# Member 1: Lead Cloud & DevOps Engineer
# ============================================================================

@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for cloud load balancers and monitoring services.
    Checks database connectivity, cache status, and basic system health.
    
    Returns:
        - 200 OK: System is healthy
        - 503 Service Unavailable: One or more services are down
    """
    health_status = {
        'status': 'healthy',
        'services': {},
    }
    
    # Check Database Connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health_status['services']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['services']['database'] = f'error: {str(e)}'
    
    # Check Cache Connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['services']['cache'] = 'ok'
        else:
            raise Exception('Cache key retrieval failed')
    except Exception as e:
        health_status['status'] = 'degraded'
        health_status['services']['cache'] = f'warning: {str(e)}'
    
    # Set appropriate HTTP status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)