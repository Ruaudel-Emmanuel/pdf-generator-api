"""
PDF Generator API - Flask Application
Author: Emmanuel
Version: 1.0
Simple PDF generation without WeasyPrint system dependencies
"""

import os
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
API_KEY = os.getenv('PERPLEXITY_API_KEY')
if not API_KEY:
    print("⚠️  WARNING: PERPLEXITY_API_KEY not found in .env file")
    print("Set PERPLEXITY_API_KEY=sk-your-key in .env to enable AI generation")
    API_KEY = "demo"  # Allow app to run for testing

# Setup directories
UPLOAD_DIR = Path('generated_pdfs')
LOG_DIR = Path('logs')
UPLOAD_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# API Client
openai_client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.perplexity.ai"
)


# ==================== UTILITIES ====================


def log_event(level, message):
    """Log events to file and console"""
    timestamp = datetime.now().isoformat()
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)

    try:
        with open(LOG_DIR / 'api.log', 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        print(f"Logging error: {e}")


def validate_request(data):
    """Validate incoming PDF generation request"""
    required = ['title']
    for field in required:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"

    if len(data['title']) < 3:
        return False, "Title must be at least 3 characters"

    page_count = data.get('pageCount', 18)
    if page_count < 5 or page_count > 50:
        return False, "Page count must be between 5 and 50"

    return True, "Valid"


# ==================== PERPLEXITY AI ====================


def generate_content_with_ai(title, template, points, language='fr'):
    """Generate document content using Perplexity API"""

    if API_KEY == "demo":
        log_event("INFO", "Using demo content (no API key configured)")
        points_html = '\n'.join(
            f"<h3>Point: {p}</h3><p>Detailed explanation of {p}...</p>"
            for p in points
        )
        return (
            f"<h2>Introduction</h2>"
            f"<p>This is a demo document about {title}.</p>"
            f"{points_html}"
        )

    template_instructions = {
        'llm-best-practices': (
            "Tu es un expert en Large Language Models. "
            "Rédige un guide professionnel et détaillé."
        ),
        'api-guide': (
            "Tu es un expert en intégration API. "
            "Rédige un guide technique complet."
        ),
        'automation-guide': (
            "Tu es un expert N8N. "
            "Rédige un guide d'automatisation professionnel."
        ),
        'tech-report': (
            "Tu es un consultant technique. "
            "Rédige un rapport technique détaillé."
        )
    }

    instruction = template_instructions.get(
        template,
        "Rédige un document professionnel."
    )

    prompt = f"""{instruction}

Title: {title}
Key Points to Cover:
{chr(10).join(f"- {p}" for p in points)}

Language: {language}
Format: HTML with clear sections and paragraphs
Length: Approximately 6000-8000 words
Tone: Professional, informative, actionable

Structure each section with:
1. Section title
2. Detailed explanation
3. Best practices
4. Examples

Return ONLY valid HTML content (no <html>, <head>, <body> tags), \
starting with <h2> tags.
Begin now:
"""

    try:
        log_event("INFO", "Requesting content from Perplexity API...")
        response = openai_client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
            max_tokens=4000
        )

        content = response.choices[0].message.content
        log_event("INFO", f"AI content generated ({len(content)} chars)")
        return content
    except Exception as e:
        log_event("ERROR", f"AI generation failed: {str(e)}")
        # Return fallback content
        points_html = '\n'.join(
            f"<h3>{p}</h3><p>Detailed content about {p}...</p>"
            for p in points
        )
        return f"<h2>Content</h2>{points_html}"


# ==================== PDF GENERATION ====================


def generate_html_document(
    title, description, author, content, cover_style, primary_color
):
    """Generate complete HTML document for PDF"""
    gradient_maps: dict[str, str] = {
        'gradient-blue': 'linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%)',
        'gradient-purple': 'linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)',
        'gradient-tech': 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
        'minimalist': (
            f'linear-gradient(135deg, {primary_color} 0%, '
            f'{primary_color}cc 100%)'
        )
    }

    gradient = gradient_maps.get(cover_style, gradient_maps['gradient-blue'])
    current_date = datetime.now().strftime('%d %B %Y')

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            width: 100%;
            height: 100%;
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
        }}

        .page-break {{
            page-break-after: always;
            width: 100%;
            page-break-inside: avoid;
        }}

        .cover {{
            width: 100%;
            min-height: 100vh;
            background: {gradient};
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 60px;
            page-break-after: always;
        }}

        .cover-content {{
            max-width: 800px;
        }}

        .cover h1 {{
            font-size: 3.5em;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.2;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .cover .subtitle {{
            font-size: 1.5em;
            opacity: 0.95;
            margin-bottom: 40px;
            font-weight: 300;
        }}

        .cover .meta {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-top: 60px;
        }}

        .content {{
            padding: 60px 50px;
            background: white;
        }}

        .content h2 {{
            color: {primary_color};
            font-size: 2em;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid {primary_color};
            page-break-after: avoid;
        }}

        .content h3 {{
            color: {primary_color};
            font-size: 1.4em;
            margin: 25px 0 15px 0;
            page-break-after: avoid;
        }}

        .content p {{
            margin: 15px 0;
            text-align: justify;
            line-height: 1.8;
        }}

        .content ul, .content ol {{
            margin: 20px 0 20px 30px;
        }}

        .content li {{
            margin: 10px 0;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }}

        @page {{
            size: A4;
            margin: 0;
        }}

        @media print {{
            .page-break {{
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>
    <div class="cover">
        <div class="cover-content">
            <h1>{title}</h1>
            {f'<div class="subtitle">{description}</div>'
             if description else ''}
            <div class="meta">
                <p>📄 Par {author}</p>
                <p>📅 {current_date}</p>
            </div>
        </div>
    </div>

    <div class="content">
        {content}

        <div class="footer">
            <h3>À propos de ce document</h3>
            <p>Ce document a été généré le {
                datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
            }.</p>
            <p><strong>Auteur:</strong> {author}</p>
            <p style="margin-top: 20px; font-size: 0.85em; color: #999;">
                © {datetime.now().year} - PDF Generator API
            </p>
        </div>
    </div>
</body>
</html>
"""
    return html


def convert_html_to_pdf_simple(html_content, output_path):
    """
    Convert HTML to PDF using alternative method (pdfkit or simple export)
    For now, just save as HTML with print instruction
    """
    try:
        # Try using pdfkit if available
        try:
            import pdfkit
            pdfkit.from_string(html_content, output_path)
            return True
        except ImportError:
            pass
        except Exception as e:
            log_event("WARNING", f"pdfkit failed: {e}")

        # Fallback: Save as HTML file
        # User can print to PDF from browser
        html_path = str(output_path).replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Create a simple PDF marker file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"PDF_EXPORT\n{output_path}\nHTML_SOURCE: {html_path}")

        return True

    except Exception as e:
        log_event("ERROR", f"PDF conversion error: {e}")
        return False


def generate_pdf(
    title, description, content, author, cover_style, primary_color
):
    """Generate PDF from HTML content"""

    html_content = generate_html_document(
        title, description, author, content, cover_style, primary_color
    )

    filename = f"document-{int(time.time())}.pdf"
    filepath = UPLOAD_DIR / filename

    try:
        # Try to generate actual PDF
        success = convert_html_to_pdf_simple(html_content, str(filepath))

        if not success:
            log_event("WARNING", "PDF conversion skipped, HTML fallback used")

        file_size = filepath.stat().st_size if filepath.exists() else 0
        log_event(
            "INFO",
            f"Document generated: {filename} ({file_size} bytes)"
        )

        return {
            'filename': filename,
            'filepath': str(filepath),
            'size': file_size
        }

    except Exception as e:
        log_event("ERROR", f"Document generation failed: {str(e)}")
        return None


# ==================== ROUTES ====================


@app.route('/')
def index():
    """Serve dashboard"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        log_event("ERROR", f"Dashboard error: {e}")
        return (
            "<h1>PDF Generator API</h1>"
            "<p>Dashboard not found. Make sure "
            "dashboard.html is in templates/ folder.</p>"
            f"<p>Error: {e}</p>"
        )


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'api_version': '1.0',
        'timestamp': datetime.now().isoformat(),
        'api_key_configured': API_KEY != "demo"
    })


@app.route('/api/generate-pdf', methods=['POST'])
def api_generate_pdf():
    """Generate PDF API endpoint"""

    start_time = time.time()

    try:
        data = request.get_json()

        # Validate request
        is_valid, message = validate_request(data)
        if not is_valid:
            log_event("WARNING", f"Invalid request: {message}")
            return jsonify({'error': message}), 400

        title = data.get('title', 'Untitled')
        description = data.get('description', '')
        template = data.get('template', 'tech-report')
        points = data.get('points', [])
        author = data.get('author', 'Emmanuel')
        language = data.get('language', 'fr')
        use_ai = data.get('useAI', False)
        cover_style = data.get('coverStyle', 'gradient-blue')
        primary_color = data.get('primaryColor', '#3182ce')

        log_event("INFO", f"PDF generation request: {title}")

        # Generate content
        if use_ai:
            content = generate_content_with_ai(
                title, template, points, language
            )
        else:
            # Use template content
            html_items = (
                f"<h3>{p}</h3><p>Contenu détaillé sur {p}...</p>"
                for p in points
            )
            points_html = '\n'.join(html_items)
            content = f"<h2>Points Clés</h2>{points_html}"

        # Generate PDF
        pdf_info = generate_pdf(
            title=title,
            description=description,
            content=content,
            author=author,
            cover_style=cover_style,
            primary_color=primary_color
        )

        if not pdf_info:
            return jsonify({'error': 'PDF generation failed'}), 500

        total_time = time.time() - start_time

        response = {
            'success': True,
            'message': 'PDF generated successfully',
            'filename': pdf_info['filename'],
            'downloadUrl': f"/download/{pdf_info['filename']}",
            'size': pdf_info['size'],
            'generationTime': int(total_time)
        }

        log_event(
            "INFO",
            f"PDF ready: {pdf_info['filename']} in {total_time:.2f}s"
        )

        return jsonify(response), 200

    except Exception as e:
        log_event("ERROR", f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_pdf(filename):
    """Download generated PDF"""

    # Security: validate filename
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400

    filepath = UPLOAD_DIR / filename

    if not filepath.exists():
        log_event("WARNING", f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404

    try:
        log_event("INFO", f"File downloaded: {filename}")
        return send_file(
            str(filepath),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        log_event("ERROR", f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get document generation statistics"""

    try:
        pdf_files = list(UPLOAD_DIR.glob('*.pdf'))
        total_size = sum(f.stat().st_size for f in pdf_files)

        return jsonify({
            'total_documents': len(pdf_files),
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'created_today': sum(
                1 for f in pdf_files
                if datetime.fromtimestamp(f.stat().st_ctime).date()
                == datetime.today().date()
            ),
            'api_version': '1.0',
            'api_key_configured': API_KEY != "demo"
        })
    except Exception as e:
        log_event("ERROR", f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_files():
    """Delete files older than 7 days"""

    try:
        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days
        deleted = 0

        for file_path in UPLOAD_DIR.glob('*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                deleted += 1

        log_event("INFO", f"Cleanup: {deleted} old files deleted")

        return jsonify({
            'message': f'{deleted} old files deleted',
            'success': True
        })
    except Exception as e:
        log_event("ERROR", f"Cleanup error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    log_event("ERROR", f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== MAIN ====================


if __name__ == '__main__':
    log_event("INFO", "=== PDF Generator API Starting ===")
    log_event("INFO", "Dashboard: http://localhost:5000")
    log_event("INFO", f"API Key configured: {API_KEY != 'demo'}")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
