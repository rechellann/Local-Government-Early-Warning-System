from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class HealthCheckView(APIView):
    """Health check endpoint for deployment monitoring"""
    
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        """Check if application and database are healthy"""
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            return Response({
                'status': 'healthy',
                'message': 'API is running and database is connected',
                'database': 'connected'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'message': str(e),
                'database': 'disconnected'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

