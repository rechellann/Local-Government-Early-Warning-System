from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db import connection

from .forms import IncidentForm, HazardImageFormSet

from .models import (
    Incident,
    SensorData,
    HazardReport
)

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


# =========================================================
# DASHBOARD (UI)
# =========================================================
def dashboard(request):

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


# =========================================================
# MY REPORTS
# =========================================================
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


# =========================================================
# CREATE INCIDENT (UI)
# =========================================================
def create_incident(request):

    if request.method == 'POST':

        form = IncidentForm(request.POST)

        if form.is_valid():

            incident = form.save(
                commit=False
            )

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


# =========================================================
# INCIDENT LIST API
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_list_api(request):

    user = request.user
    groups = get_user_roles(user)

    incidents = Incident.objects.all().order_by(
        '-created_at'
    )

    if 'LGU Admin' in groups:
        pass

    elif 'Dispatcher' in groups:
        incidents = incidents.exclude(
            status='NORMAL'
        )

    elif 'Public Viewer' in groups:
        incidents = incidents.exclude(
            status='CRITICAL'
        )

    else:
        return Response(
            {
                "error": "No role assigned"
            },
            status=403
        )

    data = []

    for incident in incidents:

        item = {
            "id": incident.id,
            "title": incident.title,
            "status": incident.status,
            "created_at": incident.created_at,
        }

        if 'LGU Admin' in groups:

            item["description"] = (
                incident.description
            )

            item["images"] = (
                IncidentSerializer(
                    incident
                ).data["images"]
            )

        elif 'Dispatcher' in groups:

            item["description"] = (
                incident.description[:80]
                + "..."
            )

        data.append(item)

    return Response(
        {
            "user": user.username,
            "roles": groups,
            "count": len(data),
            "data": data
        }
    )


# =========================================================
# INCIDENT DETAIL API
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_detail_api(request, pk):

    user = request.user
    groups = get_user_roles(user)

    try:

        incident = Incident.objects.get(
            pk=pk
        )

        if (
            'Public Viewer' in groups and
            incident.status == 'CRITICAL'
        ):
            return Response(
                {
                    "error":
                    "Access denied for critical incidents"
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

            data["description"] = (
                incident.description
            )

            data["images"] = (
                IncidentSerializer(
                    incident
                ).data["images"]
            )

        elif 'Dispatcher' in groups:

            data["description"] = (
                incident.description[:100]
                + "..."
            )

        return Response(
            {
                "user": user.username,
                "roles": groups,
                "data": data
            }
        )

    except Incident.DoesNotExist:

        return Response(
            {
                "error": "Incident not found"
            },
            status=404
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
@require_http_methods(["POST"])
def bulk_update_status(request):

    groups = get_user_roles(
        request.user
    )

    if 'LGU Admin' not in groups:

        return JsonResponse(
            {
                'error':
                'Unauthorized'
            },
            status=403
        )

    selected_ids = request.POST.getlist(
        'incident_ids'
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