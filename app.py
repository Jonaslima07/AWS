import os
import uuid
import json
import boto3
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações AWS
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
S3_BUCKET = os.getenv('S3_BUCKET')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE')
LAMBDA_FUNCTION = os.getenv('LAMBDA_FUNCTION')

# Validação das variáveis obrigatórias
if not all([S3_BUCKET, DYNAMODB_TABLE, LAMBDA_FUNCTION]):
    raise ValueError("Alguma variável de ambiente obrigatória não foi definida (S3_BUCKET, DYNAMODB_TABLE, LAMBDA_FUNCTION).")

# Clientes AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

# Rotas
@app.route('/')
def check():
    return jsonify({'status': 'funcionando'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/register', methods=['POST'])
def register_user():
    try:
        # Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        photo = request.files.get('photo')
        
        if not all([name, email, photo]):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Gerar ID único para o usuário
        user_id = str(uuid.uuid4())
        
        # Upload da foto para o S3
        filename = secure_filename(photo.filename)
        s3_key = f"users/{user_id}/{filename}"
        
        s3_client.upload_fileobj(
            photo, 
            S3_BUCKET, 
            s3_key,
            ExtraArgs={'ACL': 'public-read'}  # Tornar a imagem pública (opcional)
        )
        
        photo_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        
        # Chamar a função Lambda para processar o registro
        payload = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'photo_url': photo_url
        }
        
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Verificar resposta da Lambda
        try:
            response_payload = json.loads(response['Payload'].read())
        except json.JSONDecodeError:
            response_payload = {"error": "Resposta inválida da Lambda"}
        
        if response['StatusCode'] == 200:
            return jsonify({
                'message': 'Usuário registrado com sucesso',
                'user_id': user_id,
                'photo_url': photo_url
            }), 200
        else:
            return jsonify({
                'error': 'Erro ao processar registro',
                'details': response_payload
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        response = table.scan()
        users = response.get('Items', [])
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Exibir IP público e Health Check dinamicamente
try:
    public_ip = requests.get('https://checkip.amazonaws.com').text.strip()
    print(f"IP Público: {public_ip}")
    print(f"Health Check: http://{public_ip}:5000/health")
except Exception as e:
    print(f"Não foi possível obter IP público: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
