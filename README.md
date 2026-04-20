# Kasparo Backend API

A FastAPI wrapper service for the Ollama local LLM model. This backend provides RESTful API endpoints to interact with the Ollama model serving `deepseek-r1:32b` and other models.

## 📋 Overview

This backend service:
- Wraps the Ollama API with FastAPI
- Provides clean, documented REST endpoints
- Handles error cases gracefully
- Supports CORS for frontend integration
- Includes health checks and model listing
- Provides automatic API documentation (Swagger UI & ReDoc)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Ollama running locally at `http://100.127.36.42:11434`
- `deepseek-r1:32b` model pulled in Ollama

### Installation

1. **Navigate to the backend folder:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file (optional):**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` if you need to change the Ollama URL or other settings.

5. **Run the server:**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📚 API Endpoints

### 1. Health Check
**GET** `/health`

Check if the backend and Ollama service are running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Backend and Ollama service are running",
  "service_url": "http://100.127.36.42:11434"
}
```

---

### 2. Generate Text
**POST** `/api/generate`

Generate text using the Ollama model.

**Request Body:**
```json
{
  "prompt": "What is quantum computing?",
  "model": "deepseek-r1:32b",
  "stream": false,
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40
}
```

**Parameters:**
- `prompt` (string, required): The prompt to send to the model
- `model` (string, optional): Model name (uses default if not specified)
- `stream` (boolean, optional, default: false): Whether to stream the response
- `temperature` (float, optional): Controls randomness (0-1)
- `top_p` (float, optional): Nucleus sampling parameter
- `top_k` (int, optional): Top-k sampling parameter

**Response:**
```json
{
  "model": "deepseek-r1:32b",
  "response": "Quantum computing harnesses quantum mechanics principles...",
  "created_at": "2026-04-21T10:30:00Z",
  "done": true,
  "total_duration": 2500000000,
  "load_duration": 500000000,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 800000000,
  "eval_count": 50,
  "eval_duration": 1200000000
}
```

---

### 3. Generate with History
**POST** `/api/generate-with-history`

Generate text with conversation history context.

**Query Parameters:**
- `history` (string, optional): Previous conversation context

**Request Body:**
Same as `/api/generate`

---

### 4. List Available Models
**GET** `/api/models`

List all available models on the Ollama service.

**Response:**
```json
{
  "models": [
    {
      "name": "deepseek-r1:32b",
      "modified_at": "2026-04-21T10:00:00Z",
      "size": 36700000000
    }
  ]
}
```

---

### 5. Root Endpoint
**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "name": "Kasparo Backend API",
  "version": "1.0.0",
  "description": "FastAPI wrapper for Ollama LLM Model",
  "endpoints": {
    "health": "/health",
    "generate": "/api/generate",
    "models": "/api/models",
    "docs": "/docs",
    "redoc": "/redoc"
  }
}
```

---

## 🔧 Configuration

All configuration is managed via environment variables. See `.env.example` for available options.

### Key Configuration Variables:

```env
# API Configuration
HOST=0.0.0.0           # Server host
PORT=8000              # Server port
DEBUG=False            # Debug mode

# Ollama Configuration
OLLAMA_BASE_URL=http://100.127.36.42:11434  # Ollama service URL
DEFAULT_MODEL=deepseek-r1:32b                # Default model to use
REQUEST_TIMEOUT=600                          # Request timeout in seconds

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]  # Allowed origins
```

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application and endpoints
├── config.py               # Configuration settings
├── models.py               # Pydantic request/response models
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🧪 Testing

### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Generate text
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "model": "deepseek-r1:32b",
    "stream": false
  }'

# List models
curl http://localhost:8000/api/models
```

### Using Python:

```python
import requests

url = "http://localhost:8000/api/generate"
payload = {
    "prompt": "Explain machine learning in 100 words",
    "model": "deepseek-r1:32b",
    "stream": False
}

response = requests.post(url, json=payload)
print(response.json()["response"])
```

### Using Postman or API Client:
1. Open http://localhost:8000/docs
2. Click on the endpoint you want to test
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

## 🐛 Troubleshooting

### Issue: Connection refused to Ollama
**Solution:** Make sure Ollama is running at the configured URL:
```bash
# Check if Ollama is accessible
curl http://100.127.36.42:11434/api/tags
```

### Issue: Model not found
**Solution:** Verify the model is pulled in Ollama:
```bash
# Pull the model
ollama pull deepseek-r1:32b
```

### Issue: Request timeout
**Solution:** Increase `REQUEST_TIMEOUT` in config.py or .env file. Large models may take longer to process.

### Issue: CORS errors from frontend
**Solution:** Add your frontend URL to `CORS_ORIGINS` in config.py or .env file.

## 📦 Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation using Python type annotations
- **pydantic-settings**: Settings management
- **requests**: HTTP library for calling Ollama API
- **python-dotenv**: Load environment variables from .env file

## 🔐 Security Considerations

- The backend connects to Ollama without authentication. If deploying to production, consider:
  - Adding API authentication (API keys, JWT tokens)
  - Using HTTPS
  - Restricting CORS origins
  - Adding rate limiting
  - Validating and sanitizing inputs

## 📈 Performance Tips

1. **Model Selection**: Choose appropriate model sizes for your hardware
2. **Timeout Configuration**: Adjust `REQUEST_TIMEOUT` based on model complexity
3. **Temperature Settings**: Lower values (0.1-0.3) for factual tasks, higher (0.7-1.0) for creative tasks
4. **Caching**: Consider implementing response caching for repeated queries

## 🤝 Integration with Frontend

The backend is CORS-enabled by default for local development. To connect from a frontend (React, Vue, etc.):

```javascript
// JavaScript fetch example
const response = await fetch('http://localhost:8000/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'Your prompt here',
    model: 'deepseek-r1:32b',
    stream: false
  })
});

const data = await response.json();
console.log(data.response);
```

## 📝 License

This project is provided as-is for the Kasparo project.

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify Ollama is running properly
3. Check the logs from the FastAPI server
4. Review the automatic API documentation at `/docs`

---

**Happy coding! 🎉**
