"""
Example usage of the Kasparo Backend API

This file demonstrates various ways to interact with the backend API
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def example_health_check():
    """Example: Check backend health"""
    print("\n=== Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))


def example_simple_generation():
    """Example: Simple text generation"""
    print("\n=== Simple Text Generation ===")
    
    payload = {
        "prompt": "What is the capital of France?",
        "model": "deepseek-r1:32b",
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/api/generate", json=payload)
    result = response.json()
    
    print(f"Prompt: {payload['prompt']}")
    print(f"Response: {result['response']}")
    print(f"Time taken: {result['total_duration'] / 1_000_000_000:.2f}s")


def example_generation_with_temperature():
    """Example: Generation with temperature control"""
    print("\n=== Generation with Temperature ===")
    
    payload = {
        "prompt": "Write a creative short story about a robot",
        "model": "deepseek-r1:32b",
        "stream": False,
        "temperature": 0.8  # Higher temperature for more creative output
    }
    
    response = requests.post(f"{BASE_URL}/api/generate", json=payload)
    result = response.json()
    
    print(f"Prompt: {payload['prompt']}")
    print(f"Response: {result['response'][:200]}...")  # Show first 200 chars
    print(f"Model: {result['model']}")


def example_factual_query():
    """Example: Factual query with lower temperature"""
    print("\n=== Factual Query (Low Temperature) ===")
    
    payload = {
        "prompt": "What is the atomic number of gold?",
        "model": "deepseek-r1:32b",
        "stream": False,
        "temperature": 0.2  # Lower temperature for more factual output
    }
    
    response = requests.post(f"{BASE_URL}/api/generate", json=payload)
    result = response.json()
    
    print(f"Prompt: {payload['prompt']}")
    print(f"Response: {result['response']}")


def example_list_models():
    """Example: List available models"""
    print("\n=== List Available Models ===")
    
    response = requests.get(f"{BASE_URL}/api/models")
    result = response.json()
    
    if "models" in result:
        for model in result["models"]:
            print(f"- {model['name']} ({model['size']} bytes)")
    else:
        print("No models found")


def example_api_root():
    """Example: Get API information"""
    print("\n=== API Root Information ===")
    
    response = requests.get(f"{BASE_URL}/")
    result = response.json()
    
    print(f"Name: {result['name']}")
    print(f"Version: {result['version']}")
    print(f"Endpoints:")
    for endpoint, path in result['endpoints'].items():
        print(f"  {endpoint}: {path}")


def example_error_handling():
    """Example: Error handling"""
    print("\n=== Error Handling ===")
    
    # Try to connect to a non-existent endpoint
    try:
        response = requests.get(f"{BASE_URL}/invalid", timeout=5)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Details: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the backend")
    except requests.exceptions.Timeout:
        print("Error: Request timed out")


def example_generation_with_context():
    """Example: Generation with conversation history"""
    print("\n=== Generation with Context ===")
    
    history = "Q: What is Python?\nA: Python is a programming language."
    payload = {
        "prompt": "What are its main uses?",
        "model": "deepseek-r1:32b",
        "stream": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/generate-with-history",
        json=payload,
        params={"history": history}
    )
    result = response.json()
    
    print(f"History: {history}")
    print(f"Prompt: {payload['prompt']}")
    print(f"Response: {result['response']}")


def example_benchmark():
    """Example: Benchmark model performance"""
    print("\n=== Performance Benchmark ===")
    
    prompts = [
        "What is 2+2?",
        "Explain machine learning",
        "Tell me a joke"
    ]
    
    for prompt in prompts:
        payload = {
            "prompt": prompt,
            "model": "deepseek-r1:32b",
            "stream": False
        }
        
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        result = response.json()
        
        duration_seconds = result['total_duration'] / 1_000_000_000
        print(f"Prompt: '{prompt}' -> Time: {duration_seconds:.2f}s")


if __name__ == "__main__":
    print("Kasparo Backend API - Example Usage")
    print("=====================================")
    
    try:
        # Run all examples
        example_health_check()
        example_api_root()
        example_list_models()
        example_simple_generation()
        example_generation_with_temperature()
        example_factual_query()
        example_error_handling()
        example_benchmark()
        
        print("\n\n✅ All examples completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the backend")
        print("Make sure the backend is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
