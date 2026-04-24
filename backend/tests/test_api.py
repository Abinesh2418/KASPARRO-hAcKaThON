"""
API tests for Curio backend.
Run: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
            response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "groq" in data
        assert "ollama" in data

    def test_root_returns_api_info(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == "Curio API"


class TestProducts:
    def test_list_all_products(self):
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert len(data["products"]) > 0

    def test_filter_by_category(self):
        response = client.get("/api/v1/products?category=tops")
        assert response.status_code == 200
        products = response.json()["products"]
        assert all(p["category"] == "tops" for p in products)

    def test_limit_parameter(self):
        response = client.get("/api/v1/products?limit=3")
        assert response.status_code == 200
        assert len(response.json()["products"]) <= 3


class TestPreferences:
    def test_unknown_session_returns_404(self):
        response = client.get("/api/v1/preferences/nonexistent-session")
        assert response.status_code == 404


class TestVisualSearch:
    def test_rejects_non_image(self):
        response = client.post(
            "/api/v1/visual-search",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 400

    def test_accepts_jpeg_and_returns_attributes(self):
        # Uses mock fallback since Ollama may not be running
        with open("tests/fixtures/sample.jpg", "rb") as f:
            img = f.read()
        response = client.post(
            "/api/v1/visual-search",
            files={"file": ("sample.jpg", img, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "attributes" in data
        assert "products" in data
