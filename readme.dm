# PDF Generator API

Professional PDF generation service powered by Python/Flask and Perplexity AI.

## Features

- 🤖 **AI-Powered Content**: Generate document content using Perplexity API
- 📄 **Professional PDFs**: Beautiful 18-page documents with custom covers
- 🎨 **Customizable Design**: Multiple cover styles and color schemes
- ⚡ **Fast Generation**: Optimized PDF rendering with WeasyPrint
- 🔒 **Secure**: API key stored server-side in .env
- 📊 **Statistics**: Track PDF generation metrics
- 🗂️ **Auto Cleanup**: Automatic removal of old files

## Quick Start

### Prerequisites

- Python 3.9+
- pip or conda
- Perplexity API key

### Installation

1. **Clone or download the project**
git clone 
cd pdf-generator-api

2. **Create virtual environment**
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
pip install -r requirements.txt

4. **Configure environment**
cp .env.example .env
# Edit .env and add your PERPLEXITY_API_KEY

5. **Run the server**
python app.py

Server will start at: http://localhost:5000

## API Endpoints

### Generate PDF
**POST** `/api/generate-pdf`

Generate a new PDF document with optional AI content generation.

**Request:**
{
  "title": "LLM Best Practices",
  "description": "Complete guide to Large Language Models",
  "template": "llm-best-practices",
  "points": ["Point 1", "Point 2"],
  "author": "Your Name",
  "language": "fr",
  "useAI": true,
  "pageCount": 18,
  "coverStyle": "gradient-blue",
  "primaryColor": "#3182ce",
  "paperFormat": "a4"
}

**Response (200):**
{
  "success": true,
  "message": "PDF generated successfully",
  "filename": "document-1706292016.pdf",
  "downloadUrl": "/download/document-1706292016.pdf",
  "size": 1250000,
  "generationTime": 45
}

### Download PDF
**GET** `/download/`

Download a generated PDF file.

**Example:**
curl -O http://localhost:5000/download/document-1706292016.pdf

### Statistics
**GET** `/api/stats`

Get PDF generation statistics.

**Response:**
{
  "total_pdfs": 42,
  "total_size_mb": 125.5,
  "created_today": 3,
  "api_version": "1.0"
}

### Health Check
**GET** `/health`

Check API status.

**Response:**
{
  "status": "ok",
  "api_version": "1.0",
  "timestamp": "2024-01-27T10:30:45"
}

### Cleanup Old Files
**POST** `/api/cleanup`

Delete PDFs older than 7 days.

**Response:**
{
  "message": "5 old PDFs deleted",
  "success": true
}

## Usage Examples

### Python
import requests

response = requests.post('http://localhost:5000/api/generate-pdf', json={
    'title': 'LLM Best Practices',
    'template': 'llm-best-practices',
    'useAI': True,
    'author': 'Emmanuel'
})

data = response.json()
print(f"PDF ready: {data['downloadUrl']}")

### cURL
curl -X POST http://localhost:5000/api/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API Integration Guide",
    "template": "api-guide",
    "useAI": true
  }'

### JavaScript/Fetch
const response = await fetch('http://localhost:5000/api/generate-pdf', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'N8N Automation Guide',
    template: 'automation-guide',
    useAI: true
  })
});

const data = await response.json();
window.location.href = data.downloadUrl;

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PERPLEXITY_API_KEY | required | Your Perplexity API key |
| FLASK_ENV | production | Flask environment |
| API_HOST | 0.0.0.0 | API server host |
| API_PORT | 5000 | API server port |
| DEFAULT_LANGUAGE | fr | Default document language |
| DEFAULT_AUTHOR | Your Company | Default document author |
| DEFAULT_COVER_STYLE | gradient-blue | Default cover design |
| DEFAULT_PAGE_COUNT | 18 | Default page count |

### Available Templates

- **llm-best-practices**: Large Language Models guide
- **api-guide**: API integration documentation
- **automation-guide**: N8N automation workflows
- **tech-report**: Technical report template

### Cover Styles

- `gradient-blue`: Modern blue gradient
- `gradient-purple`: Purple gradient
- `gradient-tech`: Tech-inspired gradient
- `minimalist`: Minimal design

## Project Structure

pdf-generator-api/
├── app.py                      # Main Flask application
├── .env                        # Environment variables (create from .env.example)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── dashboard.html          # Web interface
├── static/
│   └── css/
│       └── style.css
├── pdf_templates/              # PDF generation templates
├── generated_pdfs/             # Output directory for PDFs
└── logs/                       # Application logs


## Deployment

### Using Gunicorn (Production)

pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

### Using Docker

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

### Deploy on Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables in dashboard
4. Deploy automatically

## Testing

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Format code
black .

# Lint code
flake8 .

## Troubleshooting

### PDF Generation is Slow
- Reduce `pageCount` parameter
- Simplify content formatting
- Check server resources

### API Key Not Found
- Ensure `.env` file exists
- Verify `PERPLEXITY_API_KEY` is set
- Check file permissions

### WeasyPrint Errors
- Install required system packages
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpango-gobject-0

# macOS
brew install pango

### CORS Issues
- Flask-CORS is configured to allow all origins
- Modify `CORS(app)` in app.py if needed

## Performance Tips

1. **Batch Requests**: Generate multiple PDFs in parallel
2. **Use Templates**: Set `useAI=false` to skip AI generation
3. **Reduce Pages**: Lower `pageCount` for faster generation
4. **Cache Results**: Store generated PDFs for reuse
5. **Clean Up**: Run `/api/cleanup` regularly

## Security Considerations

- API key stored server-side only
- Input validation on all endpoints
- File path validation to prevent traversal attacks
- CORS enabled but can be restricted
- No sensitive data in logs

## License

MIT License

## Support

For issues and questions:
- Check logs in `logs/api.log`
- Review API response messages
- Test endpoints with curl first

## Version History

### v1.1 (Current)
- Initial release
- PDF generation with AI support
- Multiple templates
- Statistics and cleanup

---


Made with ❤️ by Emmanuel | Powered by Flask + Perplexity AI
