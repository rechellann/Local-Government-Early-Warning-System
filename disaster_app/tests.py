from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import Incident

class SecurityRBACPathTest(TestCase):
    def setUp(self):
        # Create roles
        self.admin_group = Group.objects.create(name='LGU Admin')
        self.public_group = Group.objects.create(name='Public Viewer')
        self.dispatcher_group = Group.objects.create(name='Dispatcher')
        
        # Create users
        self.admin_user = User.objects.create_user(username='admin_user', password='password123')
        self.admin_user.groups.add(self.admin_group)
        
        self.public_user = User.objects.create_user(username='public_user', password='password123')
        self.public_user.groups.add(self.public_group)

        self.dispatcher = User.objects.create_user(username='dispatcher_user', password='password123')
        self.dispatcher.groups.add(self.dispatcher_group)
        
        # Create a critical incident
        self.critical_incident = Incident.objects.create(
            title="Flash Flood",
            description="High risk area",
            status="CRITICAL",
            created_by=self.admin_user
        )

    def test_public_cannot_access_critical_api(self):
        """Verify that Public Viewers are blocked from critical incidents in the API."""
        self.client.force_login(self.public_user)
        response = self.client.get(f'/api/incidents/{self.critical_incident.pk}/')
        # Should be 403 Forbidden based on logic in views.py
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_critical_api(self):
        """Verify LGU Admins have full access."""
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/api/incidents/{self.critical_incident.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_bulk_update_is_forbidden_and_logged(self):
        """Verify that Dispatchers cannot perform bulk updates (Active Defense check)."""
        self.client.force_login(self.dispatcher)
        # Attempting to bulk update the critical incident
        response = self.client.post('/api/incidents/bulk-update-status/', {
            'incident_ids': [self.critical_incident.id]
        })
        self.assertEqual(response.status_code, 403)
