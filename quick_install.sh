#!/bin/bash

# ============================================================================
# WordPress MCP Server - Quick Installation Script
# ============================================================================

echo "=============================================="
echo "WordPress MCP Server - Quick Installation"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION - CHANGE THESE VALUES
# ============================================================================

echo -e "${YELLOW}ВАЖНО: Перед запуском отредактируйте этот скрипт!${NC}"
echo "Откройте quick_install.sh и измените WordPress настройки:"
echo ""

# WordPress Configuration - CHANGE THESE!
WORDPRESS_URL="https://your-wordpress-site.com/"
WORDPRESS_USERNAME="your-username"
WORDPRESS_PASSWORD="your-application-password"

# Check if configuration is set
if [[ "$WORDPRESS_URL" == "https://your-wordpress-site.com/" ]]; then
    echo -e "${RED}❌ Ошибка: Настройки WordPress не изменены!${NC}"
    echo ""
    echo "Отредактируйте этот файл и измените:"
    echo "  WORDPRESS_URL=\"https://your-site.com/\""
    echo "  WORDPRESS_USERNAME=\"your-username\""
    echo "  WORDPRESS_PASSWORD=\"your-app-password\""
    echo ""
    read -p "Нажмите Enter для редактирования или Ctrl+C для выхода..."
    nano "$0"
    echo ""
    echo "Теперь запустите скрипт снова: sudo bash quick_install.sh"
    exit 1
fi

echo -e "${GREEN}✓ Настройки WordPress найдены${NC}"
echo ""

# ============================================================================
# INSTALLATION
# ============================================================================

echo -e "${BLUE}Шаг 1: Обновление системы...${NC}"
apt update && apt upgrade -y

echo ""
echo -e "${BLUE}Шаг 2: Установка зависимостей...${NC}"
apt install -y python3 python3-pip python3-venv git curl wget net-tools

echo ""
echo -e "${BLUE}Шаг 3: Клонирование проекта с GitHub...${NC}"
cd /opt
if [ -d "wordpress-mcp-server" ]; then
    echo "Директория уже существует, удаляем старую версию..."
    rm -rf wordpress-mcp-server
fi

git clone https://github.com/kolombo2903/MCP.git wordpress-mcp-server
cd wordpress-mcp-server

echo ""
echo -e "${BLUE}Шаг 4: Настройка WordPress credentials...${NC}"
sed -i "s|WORDPRESS_URL = \"https://your-wordpress-site.com/\"|WORDPRESS_URL = \"$WORDPRESS_URL\"|g" mcp_sse_server.py
sed -i "s|WORDPRESS_USERNAME = \"your-username\"|WORDPRESS_USERNAME = \"$WORDPRESS_USERNAME\"|g" mcp_sse_server.py
sed -i "s|WORDPRESS_PASSWORD = \"your-password\"|WORDPRESS_PASSWORD = \"$WORDPRESS_PASSWORD\"|g" mcp_sse_server.py

echo -e "${GREEN}✓ WordPress настройки применены:${NC}"
echo "  URL: $WORDPRESS_URL"
echo "  Username: $WORDPRESS_USERNAME"

echo ""
echo -e "${BLUE}Шаг 5: Создание Python окружения...${NC}"
python3 -m venv venv

echo ""
echo -e "${BLUE}Шаг 6: Установка Python пакетов...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "${BLUE}Шаг 7: Создание systemd сервиса...${NC}"
cat > /etc/systemd/system/wordpress-mcp-server.service <<EOF
[Unit]
Description=WordPress MCP SSE Server for OpenAI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/wordpress-mcp-server
Environment=PATH=/opt/wordpress-mcp-server/venv/bin
ExecStart=/opt/wordpress-mcp-server/venv/bin/python mcp_sse_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo -e "${BLUE}Шаг 8: Запуск MCP сервера...${NC}"
systemctl daemon-reload
systemctl enable wordpress-mcp-server
systemctl start wordpress-mcp-server

echo ""
echo -e "${BLUE}Шаг 9: Настройка firewall...${NC}"
ufw allow 8000/tcp || echo "UFW не установлен или отключен"

echo ""
echo -e "${BLUE}Шаг 10: Проверка статуса сервера...${NC}"
sleep 3
systemctl status wordpress-mcp-server --no-pager

echo ""
echo -e "${BLUE}Шаг 11: Тестирование endpoints...${NC}"
echo "Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Сервер ещё запускается..."

echo ""
echo -e "${BLUE}Шаг 12: Установка Cloudflare Tunnel...${NC}"
cd /root
if [ ! -f "/usr/local/bin/cloudflared" ]; then
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared-linux-amd64
    mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
    echo -e "${GREEN}✓ Cloudflared установлен${NC}"
else
    echo -e "${GREEN}✓ Cloudflared уже установлен${NC}"
fi

echo ""
echo "Запуск Cloudflare Tunnel..."
pkill cloudflared 2>/dev/null || true
nohup cloudflared tunnel --url http://localhost:8000 > /root/cloudflared.log 2>&1 &
sleep 5

echo ""
echo -e "${GREEN}Получение HTTPS URL...${NC}"
HTTPS_URL=$(cat /root/cloudflared.log | grep -o 'https://[^ ]*\.trycloudflare\.com' | head -1)

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "=============================================="
echo -e "${GREEN}✅ УСТАНОВКА ЗАВЕРШЕНА!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}📊 Информация о сервере:${NC}"
echo "  • MCP Server работает на порту 8000"
echo "  • WordPress URL: $WORDPRESS_URL"
echo "  • Systemd сервис: wordpress-mcp-server"
echo ""
echo -e "${BLUE}🌐 HTTPS URL для ChatGPT:${NC}"
if [ -n "$HTTPS_URL" ]; then
    echo -e "${GREEN}  $HTTPS_URL${NC}"
    echo ""
    echo -e "${YELLOW}Используйте в ChatGPT:${NC}"
    echo -e "${GREEN}  ${HTTPS_URL}/sse${NC}"
else
    echo -e "${YELLOW}  URL не найден. Проверьте логи:${NC}"
    echo "  cat /root/cloudflared.log | grep https://"
fi
echo ""
echo -e "${BLUE}🔧 Команды управления:${NC}"
echo "  Статус:      sudo systemctl status wordpress-mcp-server"
echo "  Логи:        sudo journalctl -u wordpress-mcp-server -f"
echo "  Перезапуск:  sudo systemctl restart wordpress-mcp-server"
echo "  Остановка:   sudo systemctl stop wordpress-mcp-server"
echo ""
echo -e "${BLUE}🔗 Cloudflare Tunnel:${NC}"
echo "  Логи:        cat /root/cloudflared.log"
echo "  Перезапуск:  pkill cloudflared && nohup cloudflared tunnel --url http://localhost:8000 > /root/cloudflared.log 2>&1 &"
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Готово! Подключайте к ChatGPT!${NC}"
echo "=============================================="
echo ""

