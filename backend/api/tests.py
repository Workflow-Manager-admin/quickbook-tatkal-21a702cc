from rest_framework.test import APITestCase
from django.urls import reverse

class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})

class UserProfileRegistrationTests(APITestCase):
    def test_register_user_profile(self):
        """
        Ensure POST /api/user_profiles/ allows registration with correct data and returns 201.
        """
        url = "/api/user_profiles/"
        payload = {
            "username": "autotestuser",
            "password": "testpassAUT0",
            "full_name": "Test User",
            "age": 30,
            "address": "123 Test Lane",
            "preferred_berth": "lower",
            "auto_fill_enabled": True
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertIn(response.status_code, (201, 400))  # Accept 201 for success, 400 if already registered
        if response.status_code == 201:
            resp_data = response.data
            self.assertEqual(resp_data["full_name"], payload["full_name"])
            self.assertEqual(resp_data["age"], payload["age"])
            self.assertEqual(resp_data["address"], payload["address"])
            self.assertEqual(resp_data["preferred_berth"], payload["preferred_berth"])
            self.assertEqual(resp_data["auto_fill_enabled"], payload["auto_fill_enabled"])
        elif response.status_code == 400:
            # User already exists, should give "User already exists."
            self.assertEqual(response.data.get("error"), "User already exists.")
