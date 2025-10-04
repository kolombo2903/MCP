#!/bin/bash

echo "=========================================="
echo "WordPress MCP Server - GitHub Setup"
echo "=========================================="
echo ""

# Проверка установки Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите Git:"
    echo "   sudo apt install git"
    exit 1
fi

echo "✅ Git установлен"
echo ""

# Инициализация Git репозитория
if [ ! -d .git ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    echo "✅ Git репозиторий инициализирован"
else
    echo "✅ Git репозиторий уже существует"
fi

# Настройка Git (если не настроен)
if [ -z "$(git config user.name)" ]; then
    echo ""
    read -p "Введите ваше имя для Git: " git_name
    git config user.name "$git_name"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Введите ваш email для Git: " git_email
    git config user.email "$git_email"
fi

echo ""
echo "📝 Git конфигурация:"
echo "   Имя:  $(git config user.name)"
echo "   Email: $(git config user.email)"
echo ""

# Добавление всех файлов
echo "📁 Добавление файлов в Git..."
git add .

# Создание первого коммита
if ! git rev-parse HEAD > /dev/null 2>&1; then
    echo "💾 Создание первого коммита..."
    git commit -m "Initial commit: WordPress MCP Server v1.0.0

- FastAPI server with SSE support
- 4 WordPress tools: create, update, get, delete posts
- WordPress REST API integration
- Cloudflare Tunnel support
- Systemd service configuration
- Complete documentation in Russian"
    echo "✅ Коммит создан"
else
    echo "💾 Создание коммита с изменениями..."
    git commit -m "Update project files"
    echo "✅ Коммит создан"
fi

echo ""
echo "=========================================="
echo "✅ Проект готов к публикации на GitHub!"
echo "=========================================="
echo ""
echo "СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1. Создайте новый репозиторий на GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Назовите репозиторий (например): wordpress-mcp-server"
echo ""
echo "3. НЕ добавляйте README, .gitignore или LICENSE"
echo "   (они уже есть в проекте)"
echo ""
echo "4. После создания репозитория выполните команды:"
echo ""
echo "   git remote add origin https://github.com/ВАШЕ_ИМЯ/wordpress-mcp-server.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "5. Или используйте SSH (если настроен):"
echo ""
echo "   git remote add origin git@github.com:ВАШЕ_ИМЯ/wordpress-mcp-server.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "=========================================="
echo ""
echo "💡 СОВЕТ: Не забудьте изменить 'ВАШЕ_ИМЯ' на ваш GitHub username!"
echo ""

