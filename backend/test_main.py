"""
Unit tests for the Kasparo Backend API

Run with: python -m pytest test_main.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import requests
from unittest.mock import patch, MagicMock


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check_success(self):
        """Test successful health check"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "unhealthy"]
            assert "message" in data
            assert "service_url" in data
    
    def test_health_check_returns_correct_format(self):
        """Test health check response format"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            response = client.get("/health")
            data = response.json()
            
            assert isinstance(data, dict)
            assert all(key in data for key in ["status", "message", "service_url"])


class TestGenerateEndpoint:
    """Tests for the generate endpoint"""
    
    def test_generate_success(self):
        """Test successful text generation"""
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "deepseek-r1:32b",
                "response": "Test response",
                "created_at": "2026-04-21T10:00:00Z",
                "done": True,
                "total_duration": 1000000000,
                "load_duration": 100000000,
                "prompt_eval_count": 5,
                "prompt_eval_duration": 200000000,
                "eval_count": 10,
                "eval_duration": 700000000
            }
            mock_post.return_value = mock_response
            
            payload = {
                "prompt": "Test prompt",
                "model": "deepseek-r1:32b",
                "stream": False
            }
            
            response = client.post("/api/generate", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Test response"
            assert data["model"] == "deepseek-r1:32b"
    
    def test_generate_missing_prompt(self):
        """Test generate endpoint with missing prompt"""
        payload = {
            "model": "deepseek-r1:32b"
            # prompt is missing
        }
        
        response = client.post("/api/generate", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_connection_error(self):
        """Test generate endpoint when Ollama is unavailable"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError()
            
            payload = {
                "prompt": "Test prompt",
                "model": "deepseek-r1:32b",
                "stream": False
            }
            
            response = client.post("/api/generate", json=payload)
            
            assert response.status_code == 503


class TestListModelsEndpoint:
    """Tests for the list models endpoint"""
    
    def test_list_models_success(self):
        """Test successful model listing"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "deepseek-r1:32b", "size": 36700000000}
                ]
            }
            mock_get.return_value = mock_response
            
            response = client.get("/api/models")
            
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert len(data["models"]) > 0


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestRequestValidation:
    """Tests for request validation"""
    
    def test_temperature_validation(self):
        """Test temperature parameter validation"""
        payload = {
            "prompt": "Test",
            "temperature": 1.5  # Invalid: should be 0-1
        }
        
        response = client.post("/api/generate", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_valid_temperature(self):
        """Test valid temperature values"""
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "deepseek-r1:32b",
                "response": "Test",
                "created_at": "2026-04-21T10:00:00Z",
                "done": True,
                "total_duration": 1000000000,
                "load_duration": 100000000,
                "prompt_eval_count": 5,
                "prompt_eval_duration": 200000000,
                "eval_count": 10,
                "eval_duration": 700000000
            }
            mock_post.return_value = mock_response
            
            payload = {
                "prompt": "Test",
                "temperature": 0.7
            }
            
            response = client.post("/api/generate", json=payload)
            
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
