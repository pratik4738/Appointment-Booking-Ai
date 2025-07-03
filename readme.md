# 🤖 AI Calendar Assistant

A conversational AI agent that helps users book appointments on Google Calendar through natural language interaction. Built with FastAPI, LangGraph, and Streamlit.

## ✨ Features

- 🗣️ **Natural Language Processing**: Book appointments using everyday language
- 📅 **Google Calendar Integration**: Real-time calendar availability checking
- 🤖 **Intelligent Agent**: Powered by LangGraph for sophisticated conversation flow
- 💬 **Chat Interface**: Intuitive Streamlit-based chat UI
- 🔄 **Real-time Updates**: Live calendar synchronization
- 📱 **Responsive Design**: Works on desktop and mobile

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI       │    │  Google         │
│   Frontend      │◄──►│    Backend       │◄──►│  Calendar API   │
│   (Chat UI)     │    │   (LangGraph)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Console account
- OpenAI API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-calendar-assistant
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_HOST=localhost
STREAMLIT_PORT=8501
```

### 4. Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to project root
6. Run setup script:

```bash
python google_calendar_setup.py
```

### 5. Start the Application

**Option A: Manual Start**
```bash
# Terminal 1 - Start Backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Start Frontend
streamlit run streamlit_app.py --server.port 8501
```

**Option B: Using Scripts**
```bash
# On macOS/Linux:
./start_backend.sh    # Terminal 1
./start_frontend.sh   # Terminal 2

# On Windows:
start_windows.bat     # Starts both services
```

**Option C: Docker**
```bash
docker-compose up
```

### 6. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs

## 🎯 Example Conversations

The AI agent can handle various scheduling requests:

```
User: "Hey, I want to schedule a call for tomorrow afternoon."
Agent: "I'd be happy to help you schedule a call for tomorrow afternoon! 
        Let me check your availability..."

User: "Do you have any free time this Friday?"
Agent: "Let me check your calendar for this Friday. Here are your 
        available slots: 1. Friday, December 29 at 09:00 AM..."

User: "Book a meeting between 3-5 PM next week."
Agent: "I can help you book a meeting for next week between 3-5 PM. 
        Here are some available options..."
```

## 🔧 Configuration

### Agent Customization

Modify the agent behavior in `app.py`:

```python
# Change default meeting duration
DEFAULT_MEETING_DURATION = 60  # minutes

# Modify business hours
BUSINESS_HOURS = {
    'start': 9,  # 9 AM
    'end': 17,   # 5 PM
}

# Customize agent personality
AGENT_PERSONALITY = "professional"  # casual, professional, friendly
```

### UI Customization

Modify the Streamlit interface in `streamlit_app.py`:

```python
# Change page title and icon
st.set_page_config(
    page_title="Your Calendar Assistant",
    page_icon="📅"
)

# Customize colors and styling
st.markdown("""
<style>
    .main-header {
        color: #your-color;
    }
</style>
""", unsafe_allow_html=True)
```

## 📚 API Documentation

### Main Endpoints

- `POST /chat` - Send message to calendar agent
- `GET /health` - Health check endpoint
- `GET /` - API information

### Example API Usage

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Schedule a meeting for tomorrow at 2 PM"}
)

print(response.json()["response"])
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 🔍 Troubleshooting

### Common Issues

1. **Google Calendar Connection Failed**
   - Ensure `credentials.json` is in project root
   - Run `python google_calendar_setup.py` to authenticate
   - Check Google Cloud Console API permissions

2. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` in `.env` file
   - Check API quota and billing

3. **Frontend Can't Connect to Backend**
   - Ensure backend is running on port 8000
   - Check firewall settings
   - Verify API_BASE_URL in frontend

4. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚢 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export OPENAI_API_KEY=your_key
   export API_HOST=0.0.0.0
   export API_PORT=8000
   ```

2. **Using Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Using PM2 (Node.js Process Manager)**
   ```bash
   pm2 start ecosystem.config.js
   ```

### Cloud Deployment

- **Heroku**: Use provided `Procfile`
- **AWS**: Deploy using Elastic Beanstalk
- **Google Cloud**: Use Cloud Run
- **DigitalOcean**: Use App Platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the agent framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- [Streamlit](https://streamlit.io/) for the frontend interface
- [Google Calendar API](https://developers.google.com/calendar) for calendar integration

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the `/docs` endpoint
- **Community**: Join our Discord server

---

**Built with ❤️ for seamless calendar management**