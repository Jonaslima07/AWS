from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

# Configurações AWS
S3_BUCKET = 'seus-bucket-usuarios'
AWS_REGION = 'us-east-1'
DYNAMODB_TABLE = 'Usuarios'

# Clientes AWS
s3 = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    try:
        # Dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        imagem = request.files.get('imagem')

        if not all([nome, email, imagem]):
            return jsonify({'erro': 'Dados incompletos'}), 400

        # Gerar ID único
        usuario_id = str(uuid.uuid4())
        imagem_filename = f"{usuario_id}_{secure_filename(imagem.filename)}"

        # Upload para S3
        s3.upload_fileobj(
            imagem,
            S3_BUCKET,
            imagem_filename,
            ExtraArgs={'ContentType': imagem.content_type}
        )

        # Salvar no DynamoDB
        table.put_item(
            Item={
                'usuarioId': usuario_id,
                'nome': nome,
                'email': email,
                'imagemUrl': f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{imagem_filename}",
                'imagemKey': imagem_filename,
                'dataCriacao': datetime.now().isoformat()
            }
        )

        return jsonify({
            'mensagem': 'Usuário criado com sucesso',
            'usuarioId': usuario_id
        }), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        response = table.scan()
        return jsonify(response['Items'])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)