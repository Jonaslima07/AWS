import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Flask funcionando"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Flask está funcionando perfeitamente!',
        'ip': '54.226.98.192',
        'port': 5000,
        'service': 'User Registration API'
    }), 200

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'message': 'Teste bem-sucedido!',
        'server': '54.226.98.192:5000',
        'status': 'online',
        'timestamp': '2024-01-01T00:00:00Z'
    }), 200

@app.route('/register', methods=['POST'])
def register_user():
    try:
        # Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        photo = request.files.get('photo')
        
        if not all([name, email]):
            return jsonify({'error': 'Nome e email são obrigatórios'}), 400
        
        # Gerar ID único para o usuário
        user_id = str(uuid.uuid4())
        
        # Simular upload de foto (implementação real virá depois)
        photo_url = None
        if photo:
            filename = secure_filename(photo.filename)
            photo_url = f"https://s3-projeto-aws.s3.us-east-1.amazonaws.com/simulated/{user_id}/{filename}"
        
        # Simular salvamento no banco de dados
        user_data = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'photo_url': photo_url,
            'status': 'registered_successfully',
            'message': 'Dados simulados - Configure AWS para produção'
        }
        
        return jsonify(user_data), 200
            
    except Exception as e:
        return jsonify({'error': str(e), 'details': 'Erro interno do servidor'}), 500

@app.route('/')
def home():
    return jsonify({
        'message': 'Bem-vindo à API Flask de Cadastro de Usuários',
        'version': '1.0.0',
        'endpoints': {
            'health_check': '/health (GET)',
            'register_user': '/register (POST)',
            'test': '/test (GET)'
        },
        'server_ip': '54.226.98.192',
        'documentation': 'Consulte o README para detalhes'
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIANDO SERVIDOR FLASK - USER REGISTRATION API")
    print("=" * 60)
    print("IP Público: 54.226.98.192")
    print("Porta: 5000")
    print("Health Check: http://54.226.98.192:5000/health")
    print("Teste: http://54.226.98.192:5000/test")
    print("Registro: http://54.226.98.192:5000/register")
    print("=" * 60)
    print("📊 Status: AGUARDANDO CONEXÕES...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)