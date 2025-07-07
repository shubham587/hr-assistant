import os
# Disable ChromaDB telemetry before any imports
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_service import LLMService
from query_handler import QueryHandler

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore()
llm_service = LLMService()
query_handler = QueryHandler(vector_store, llm_service)

# Ensure directories exist
os.makedirs('../data/documents', exist_ok=True)
os.makedirs('../data/chunks', exist_ok=True)
os.makedirs('../data/chroma_db', exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "HR Assistant API is running!", "status": "healthy"})

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        # Save uploaded file
        filename = file.filename
        file_path = os.path.join('../data/documents', filename)
        file.save(file_path)
        
        # Process document
        success = document_processor.process_pdf(file_path)
        
        if success:
            return jsonify({
                "message": "Document uploaded and processed successfully",
                "filename": filename
            })
        else:
            return jsonify({"error": "Failed to process document"}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": "Upload failed"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        
        # Process query and get response
        response = query_handler.process_query(user_query)
        
        return jsonify({
            "response": response.get('answer', ''),
            "sources": response.get('sources', []),
            "query": user_query
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Failed to process query"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "services": {
            "document_processor": True,
            "vector_store": vector_store.is_healthy(),
            "llm_service": llm_service.is_healthy()
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 