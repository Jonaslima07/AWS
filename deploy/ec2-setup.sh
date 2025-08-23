#!/bin/bash

# Atualizar sistema
sudo apt update -y
sudo apt upgrade -y

# Instalar Python 3 e pip
sudo apt install -y python3 python3-pip python3-venv

# Instalar Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar Nginx
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Instalar PM2 globalmente
sudo npm install -g pm2

# Criar diretórios da aplicação
mkdir -p /home/ubuntu/app/backend
mkdir -p /home/ubuntu/app/frontend

# Configurar Nginx para Ubuntu
sudo cat > /etc/nginx/sites-available/react-app << 'EOL'
server {
    listen 80;
    server_name _;
    root /home/ubuntu/app/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

# Habilitar site no Nginx
sudo ln -s /etc/nginx/sites-available/react-app /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Testar e reiniciar Nginx
sudo nginx -t
sudo systemctl restart nginx

# Configurar variáveis de ambiente
echo "export FLASK_ENV=production" >> /home/ubuntu/.bashrc
echo "export AWS_REGION=us-east-1" >> /home/ubuntu/.bashrc

# Dar permissões adequadas
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
sudo chmod -R 755 /home/ubuntu/app

# Instalar dependências do Python para Flask
sudo pip3 install flask flask-cors boto3 python-dotenv

echo "=========================================="
echo "✅ UBUNTU SERVER CONFIGURADO COM SUCESSO!"
echo "=========================================="
echo "📁 Diretórios criados:"
echo "   Backend: /home/ubuntu/app/backend"
echo "   Frontend: /home/ubuntu/app/frontend"
echo ""
echo "🌐 URL da aplicação: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/"
echo ""
echo "📋 Próximos passos:"
echo "1. Fazer upload dos arquivos da sua aplicação"
echo "2. Instalar dependências específicas"
echo "3. Iniciar a aplicação Flask com PM2"
echo "=========================================="