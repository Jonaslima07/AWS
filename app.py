import os
import uuid
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError, NoCredentialsError

app = Flask(__name__)
CORS(app)

# Configurações AWS
AWS_REGION = 'us-east-1'
S3_BUCKET_NAME = 's3-projeto-aws'  # Substitua pelo nome real do seu bucket
DYNAMODB_TABLE = 'users'

# Clientes AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Testar conexão com S3
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        
        # Testar conexão com DynamoDB
        table.table_status
        
        return jsonify({
            'status': 'healthy', 
            'message': 'Todos os serviços AWS conectados!',
            'services': {
                's3': 'connected',
                'dynamodb': 'connected',
                'flask': 'running'
            },
            'ip': '54.226.98.192'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'partial',
            'message': 'Problemas com serviços AWS',
            'error': str(e)
        }), 500

@app.route('/register', methods=['POST'])
def register_user():
    try:
        # Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        photo = request.files.get('photo')
        
        if not all([name, email]):
            return jsonify({'error': 'Nome e email são obrigatórios'}), 400
        
        if not photo:
            return jsonify({'error': 'Foto é obrigatória'}), 400

        # Gerar ID único para o usuário
        user_id = str(uuid.uuid4())
        
        # Processar upload para S3
        filename = secure_filename(photo.filename)
        s3_key = f"users/{user_id}/{filename}"
        
        # Fazer upload para S3
        s3_client.upload_fileobj(
            photo,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                'ContentType': photo.content_type,
                'ACL': 'public-read'
            }
        )
        
        # Gerar URL pública da foto
        photo_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        
        # Salvar dados no DynamoDB
        user_item = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'photo_url': photo_url,
            'created_at': str(datetime.now()),
            's3_key': s3_key
        }
        
        table.put_item(Item=user_item)
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso!',
            'user_id': user_id,
            'name': name,
            'email': email,
            'photo_url': photo_url,
            's3_bucket': S3_BUCKET_NAME,
            'dynamodb_table': DYNAMODB_TABLE
        }), 200
            
    except NoCredentialsError:
        return jsonify({'error': 'Credenciais AWS não configuradas'}), 500
    except ClientError as e:
        return jsonify({'error': f'Erro AWS: {e.response["Error"]["Message"]}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def list_users():
    try:
        response = table.scan()
        users = response.get('Items', [])
        
        return jsonify({
            'users': users,
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        response = table.get_item(Key={'user_id': user_id})
        user = response.get('Item')
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        return jsonify(user), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 API REAL COM AWS - USER REGISTRATION")
    print("=" * 60)
    print("Configurações AWS:")
    print(f"Região: {AWS_REGION}")
    print(f"Bucket S3: {S3_BUCKET_NAME}")
    print(f"Tabela DynamoDB: {DYNAMODB_TABLE}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)