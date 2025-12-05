#!/bin/bash

# YOLO目标检测Web应用部署脚本

echo "🚀 开始部署YOLO目标检测应用..."

# 1. 更新系统包
echo "📦 更新系统包..."
sudo apt update

# 2. 安装Python3和pip
echo "🐍 检查Python环境..."
sudo apt install -y python3 python3-pip python3-venv

# 3. 安装Nginx
echo "🌐 安装Nginx..."
sudo apt install -y nginx

# 4. 创建项目目录
PROJECT_DIR="/var/www/yolo-detection"
echo "📁 创建项目目录: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR

# 5. 上传项目文件到服务器
echo "📤 请将项目文件上传到: $PROJECT_DIR"
echo "   可以使用 scp 或 git clone"

# 6. 进入项目目录并创建虚拟环境
cd $PROJECT_DIR
echo "🔧 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 7. 安装Python依赖
echo "📚 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 8. 配置Nginx
echo "⚙️ 配置Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/yolo-detection
sudo ln -sf /etc/nginx/sites-available/yolo-detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 9. 创建systemd服务
echo "🔧 创建systemd服务..."
sudo tee /etc/systemd/system/yolo-detection.service > /dev/null <<EOF
[Unit]
Description=YOLO Detection Web Application
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 --timeout 300 app:app

[Install]
WantedBy=multi-user.target
EOF

# 10. 启动服务
echo "🚀 启动服务..."
sudo systemctl daemon-reload
sudo systemctl start yolo-detection
sudo systemctl enable yolo-detection

# 11. 检查服务状态
echo "✅ 检查服务状态..."
sudo systemctl status yolo-detection

echo "🎉 部署完成！"
echo "访问: http://mxxin.me"
