from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db import connection
import logging

security_logger = logging.getLogger('axes')

from .forms import IncidentForm, HazardImageFormSet

from .models import (
    Incident,
    SensorData,
    HazardReport
)

from .permissions import IsLGUAdmin, IsDispatcherOrLGUAdmin
from .serializers import (
    IncidentSerializer,
    SensorSerializer,
    HazardReportSerializer
)

# DRF
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# =========================================================
# HELPER: GET USER ROLES
# =========================================================
def get_user_roles(user):
    return list(
        user.groups.values_list(
            'name',
            flat=True
        )
    )

@login_required
def admin_dashboard(request):
    if 'LGU Admin' not in get_user_roles(request.user):
        return redirect('dashboard')

    return render(
        request,
        'dashboard/admin_dashboard.html',
        {
            'total_incidents': Incident.objects.count(),
            'critical_incidents': Incident.objects.filter(status='CRITICAL').count(),
        }
    )

@login_required 
def dashboard(request):
    incidents = Incident.objects.all().order_by('-created_at')

    return render(request, 'dashboard.html', {
        'incidents': incidents
    })

@login_required
def my_reports(request):

    incidents = Incident.objects.filter(
        created_by=request.user
    ).order_by('-created_at')

    return render(
        request,
        'dashboard.html',
        {
            'incidents': incidents
        }
    )
    
@login_required
def all_reports(request):

    groups = get_user_roles(
        request.user
    )

    if 'LGU Admin' not in groups:
        return redirect('dashboard')

    incidents = Incident.objects.all().order_by(
        '-created_at'
    )

    return render(
        request,
        'dashboard.html',
        {
            'incidents': incidents
        }
    )
@login_required
def create_incident(request):

    if request.method == 'POST':

        form = IncidentForm(request.POST)

        if form.is_valid():

            incident = form.save(commit=False)

            incident.created_by = request.user

            incident.save()

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

@login_required
def dispatcher_dashboard(request):
    if 'Dispatcher' not in get_user_roles(request.user) and 'LGU Admin' not in get_user_roles(request.user):
        return redirect('dashboard')

    return render(
        request,
        'dashboard/dispatcher_dashboard.html'
    )

@login_required
def public_dashboard(request):
    return render(
        request,
        'dashboard/public_dashboard.html'
    )

@login_required
def incident_management(request):
    groups = get_user_roles(request.user)
    if 'LGU Admin' not in groups and 'Dispatcher' not in groups:
        return redirect('dashboard')

    return render(
        request,
        'incidents/incident_management.html'
    )

def hazard_report_form(request):
    return render(
        request,
        'incidents/hazard_report_form.html'
    )

def sensor_monitoring(request):
    return render(
        request,
        'sensors/sensor_monitoring.html'
    )

def reports_analytics(request):
    return render(
        request,
        'reports/reports_analytics.html'
    )

@login_required
def audit_log(request):
    # Ensure only LGU Admins can see security audit trails
    if 'LGU Admin' not in get_user_roles(request.user):
        security_logger.warning(
            f"Unauthorized access attempt to Audit Logs by {request.user.username}"
        )
        return redirect('dashboard')

    # Pull the latest 10 failed login attempts from Axes to show in the UI
    from axes.models import AccessAttempt
    attempts = AccessAttempt.objects.all().order_by('-attempt_time')[:10]
    
    return render(
        request,
        'security/audit_log.html'
    , {'attempts': attempts})

# =========================================================
# INCIDENT LIST API
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_list_api(request):
    groups = get_user_roles(request.user)

    if 'LGU Admin' in groups or 'Dispatcher' in groups:
        incidents = Incident.objects.all().order_by('-created_at')
    else:
        # Public viewers only see non-critical incidents
        incidents = Incident.objects.exclude(status='CRITICAL').order_by('-created_at')

    serializer = IncidentSerializer(incidents, many=True)
    return Response(serializer.data)

# =========================================================
# INCIDENT DETAIL API
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_detail_api(request, pk):

    user = request.user
    groups = get_user_roles(user)

    if not groups:
        return Response(
            {
                "error": "No role assigned"
            },
            status=403
        )

    incident = get_object_or_404(Incident, pk=pk)

    # ==========================================
    # ANTI-IDOR PROTECTION
    # ==========================================
    if 'LGU Admin' not in groups and incident.created_by and incident.created_by != user:
        return Response({"error": "Unauthorized access"}, status=403)

    # Public cannot view CRITICAL incidents
    if (
        'Public Viewer' in groups
        and incident.status == 'CRITICAL'
    ):
        return Response(
            {
                "error": "Access denied for critical incidents"
            },
            status=403
        )

    data = {
        "id": incident.id,
        "title": incident.title,
        "status": incident.status,
        "created_at": incident.created_at,
    }

    if 'LGU Admin' in groups:
        data["description"] = incident.description
        data["images"] = IncidentSerializer(incident).data["images"]
    elif 'Dispatcher' in groups:
        data["description"] = incident.description[:100] + "..."

    return Response(
        {
            "user": user.username,
            "roles": groups,
            "data": data
        }
    )

# =========================================================
# INCIDENT CREATE API
# =========================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def incident_create_api(request):

    groups = get_user_roles(
        request.user
    )

    if (
        'LGU Admin' not in groups and
        'Dispatcher' not in groups
    ):
        return Response(
            {
                "error":
                "You are not allowed to create incidents"
            },
            status=403
        )

    serializer = IncidentSerializer(
        data=request.data
    )

    if serializer.is_valid():

        incident = serializer.save(
            created_by=request.user
        )

        return Response(
            {
                "message":
                "Incident created successfully",
                "data":
                IncidentSerializer(
                    incident
                ).data
            },
            status=201
        )

    return Response(
        serializer.errors,
        status=400
    )


# =========================================================
# SENSOR LIST API
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensor_list_api(request):

    sensors = SensorData.objects.all().order_by(
        '-created_at'
    )

    serializer = SensorSerializer(
        sensors,
        many=True
    )

    return Response(
        {
            "count":
            len(serializer.data),
            "data":
            serializer.data
        }
    )


# =========================================================
# SENSOR CREATE API
# =========================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sensor_create_api(request):

    serializer = SensorSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            {
                "message":
                "Sensor data created successfully",
                "data":
                serializer.data
            },
            status=201
        )

    return Response(
        serializer.errors,
        status=400
    )


# =========================================================
# HAZARD REPORT LIST API
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hazard_list_api(request):

    reports = HazardReport.objects.all().order_by(
        '-created_at'
    )

    serializer = HazardReportSerializer(
        reports,
        many=True
    )

    return Response(
        {
            "count":
            len(serializer.data),
            "data":
            serializer.data
        }
    )


# =========================================================
# HAZARD REPORT CREATE API
# =========================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hazard_create_api(request):

    serializer = HazardReportSerializer(
        data=request.data
    )

    if serializer.is_valid():

        report = serializer.save(
            reported_by=request.user
        )

        return Response(
            {
                "message":
                "Hazard report created successfully",
                "data":
                HazardReportSerializer(
                    report
                ).data
            },
            status=201
        )

    return Response(
        serializer.errors,
        status=400
    )


# =========================================================
# HEALTH CHECK
# =========================================================
@require_http_methods(["GET"])
def health_check(request):

    health_status = {
        'status': 'healthy',
        'services': {},
    }

    try:

        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')

        health_status[
            'services'
        ]['database'] = 'ok'

    except Exception as e:

        health_status[
            'status'
        ] = 'unhealthy'

        health_status[
            'services'
        ]['database'] = str(e)

    try:

        cache.set(
            'health_check',
            'ok',
            10
        )

        if cache.get(
            'health_check'
        ) == 'ok':

            health_status[
                'services'
            ]['cache'] = 'ok'

        else:
            raise Exception(
                "Cache not working properly"
            )

    except Exception as e:

        health_status[
            'status'
        ] = 'degraded'

        health_status[
            'services'
        ]['cache'] = str(e)

    status_code = (
        200
        if health_status[
            'status'
        ] == 'healthy'
        else 503
    )

    return JsonResponse(
        health_status,
        status=status_code
    )


# =========================================================
# BULK UPDATE STATUS
# =========================================================
@login_required
@require_http_methods(["POST"])
def bulk_update_status(request):
    user = request.user
    groups = get_user_roles(user)
    selected_ids = request.POST.getlist('incident_ids')

    if 'LGU Admin' not in groups:
        security_logger.warning(
            f"SECURITY ALERT: Unauthorized Bulk Update Attempt | "
            f"User: {user.username} | "
            f"IP: {request.META.get('REMOTE_ADDR')} | "
            f"Target IDs: {selected_ids}"
        )
        return JsonResponse(
            {
                'error':
                'Unauthorized'
            },
            status=403
        )

    Incident.objects.filter(
        id__in=selected_ids
    ).update(
        status='CRITICAL'
    )

    return JsonResponse(
        {
            'success': True
        }
    )
    
    