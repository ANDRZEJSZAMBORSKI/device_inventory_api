from django.test import TestCase, Client
from django.urls import reverse
import django
from django.urls import resolve
from core import views

class RoutingTest(TestCase):
    def test_health_url_reverse(self):
        client = Client()
        url = reverse("health")
        assert url == '/health/'
        response = client.get(url)
        data = response.json()
        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["request"]["path"] == "/health/"
        assert data["request"]["path_info"] == "/health/"
        assert data["META"]["REQUEST_METHOD"] == "GET"
        assert data["META"]["PATH_INFO"] == "/health/"
        assert response.request["REQUEST_METHOD"] == "GET"
        assert response.request["PATH_INFO"] == "/health/"
        assert response.wsgi_request.method == "GET"
        assert data["request"]["method"] == "GET"

        match = resolve(url)
        assert match.url_name == "health"
        assert match.func == views.health
        assert match.route == "health/"

    def test_version_url_reverse(self):
        client = Client()
        url = reverse("version")
        assert url == '/version/'
        response = client.get(url)
        data = response.json()
        assert response.status_code == 200
        assert data == {
                            "api": "device-inventory",
                            "module": "core"
                        }
        assert response.context is None

        match = resolve(url)
        assert match.url_name == "version"
        assert match.func == views.version
        assert match.route == "version/"


    def test_unknown_path_returns_404(self):
        client = Client()
        with self.assertRaises(django.urls.exceptions.NoReverseMatch):
            reverse("/definitely-not-a-route/")
        
        response = client.get("/definitely-not-a-route/")
        assert response.status_code == 404
        assert response.reason_phrase == "Not Found"
        assert response.headers == {
                                    'Content-Type': 'text/html; charset=utf-8', 
                                    'X-Frame-Options': 'DENY', 
                                    'Content-Length': '179',
                                    'X-Content-Type-Options': 'nosniff', 
                                    'Referrer-Policy': 'same-origin', 
                                    'Cross-Origin-Opener-Policy': 'same-origin'
                                    }
        expected_content = """
<!doctype html>
<html lang="en">
<head>
  <title>Not Found</title>
</head>
<body>
  <h1>Not Found</h1><p>The requested resource was not found on this server.</p>
</body>
</html>
"""
        assert response.content.decode().strip() == expected_content.strip()
        assert response.status_code == 404
        assert "<title>Not Found</title>" in response.content.decode()
        assert "<h1>Not Found</h1>" in response.content.decode()
        assert "The requested resource was not found on this server." in response.content.decode()

        with self.assertRaises(django.urls.exceptions.Resolver404):
            resolve("/definitely-not-a-route/")
            