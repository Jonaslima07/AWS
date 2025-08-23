from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/submit", methods=["POST"])
def submit():
    nome = request.form.get("nome")
    email = request.form.get("email")
    
    imagem = request.files.get("imagem")
    arquivo_nome = None
    if imagem:
        arquivo_nome = imagem.filename
        caminho = os.path.join(UPLOAD_FOLDER, arquivo_nome)
        imagem.save(caminho)
    
    return jsonify({
        "mensagem": "Dados recebidos com sucesso!",
        "nome": nome,
        "email": email,
        "arquivo": arquivo_nome
    })

# Endpoint para servir arquivos da pasta uploads
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
