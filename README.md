# WordPress MCP Server

MCP (Model Context Protocol) сервер для управления WordPress постами через ChatGPT.

## Что это?

Позволяет ChatGPT создавать, обновлять, получать и удалять посты на вашем WordPress сайте.

## Быстрый старт

### 1. Скопируйте файлы на сервер

```bash
# На вашем Ubuntu сервере создайте директорию
mkdir -p ~/wordpress-mcp-project
cd ~/wordpress-mcp-project

# Скопируйте туда эти файлы:
# - mcp_sse_server.py
# - requirements.txt
# - install.sh
```

### 2. Настройте WordPress credentials

Откройте `mcp_sse_server.py` и измените:

```python
WORDPRESS_URL = "https://your-wordpress-site.com/"
WORDPRESS_USERNAME = "your-username"
WORDPRESS_PASSWORD = "your-password"
```

**Важно:** Для `WORDPRESS_PASSWORD` используйте Application Password, а не обычный пароль:
1. В WordPress: Users → Your Profile → Application Passwords
2. Создайте новый Application Password
3. Скопируйте сгенерированный пароль

### 3. Запустите установку

```bash
chmod +x install.sh
sudo ./install.sh
```

Скрипт автоматически:
- Установит все зависимости
- Создаст виртуальное окружение Python
- Установит Python пакеты
- Создаст systemd сервис
- Запустит MCP сервер
- Установит Cloudflare Tunnel для HTTPS
- Выдаст HTTPS URL для подключения к ChatGPT

### 4. Подключите к ChatGPT

1. Откройте ChatGPT
2. Settings → Connectors → New Connector
3. Укажите:
   - **Name:** WordPress MCP
   - **URL:** `https://your-url.trycloudflare.com/sse` (из вывода install.sh)
   - **Authentication:** No authentication
4. Сохраните

### 5. Используйте!

Попросите ChatGPT:
```
Напиши статью про AI на 300 слов и опубликуй на моём WordPress сайте
```

## Архитектура

```
ChatGPT
  ↓ HTTPS/SSE
Cloudflare Tunnel
  ↓ HTTP
FastAPI MCP Server (port 8000)
  ↓ HTTPS
WordPress REST API
  ↓
WordPress Site
```

## Доступные инструменты

### 1. create_post
Создать новый пост на WordPress сайте.

**Параметры:**
- `title` (обязательно) - Заголовок поста
- `content` (обязательно) - Содержимое поста в HTML
- `excerpt` (опционально) - Краткое описание
- `status` (опционально) - Статус поста: `publish`, `draft`, `private`

**Пример использования в ChatGPT:**
```
Создай пост с заголовком "Привет, Мир!" и содержанием "<p>Это мой первый пост!</p>"
```

### 2. update_post
Обновить существующий пост.

**Параметры:**
- `post_id` (обязательно) - ID поста для обновления
- `title` (опционально) - Новый заголовок
- `content` (опционально) - Новое содержимое
- `excerpt` (опционально) - Новое описание

**Пример использования в ChatGPT:**
```
Обнови пост с ID 123, измени заголовок на "Обновлённый заголовок"
```

### 3. get_posts
Получить список постов с WordPress сайта.

**Параметры:**
- `per_page` (опционально) - Количество постов на страницу (1-100, по умолчанию 10)
- `page` (опционально) - Номер страницы (по умолчанию 1)

**Пример использования в ChatGPT:**
```
Покажи последние 5 постов с моего сайта
```

### 4. delete_post
Удалить пост с WordPress сайта.

**Параметры:**
- `post_id` (обязательно) - ID поста для удаления

**Пример использования в ChatGPT:**
```
Удали пост с ID 123
```

## Управление

### Проверка статуса
```bash
sudo systemctl status wordpress-mcp-server
```

### Просмотр логов
```bash
sudo journalctl -u wordpress-mcp-server -f
```

### Перезапуск сервера
```bash
sudo systemctl restart wordpress-mcp-server
```

### Остановка сервера
```bash
sudo systemctl stop wordpress-mcp-server
```

### Получить HTTPS URL
```bash
cat ~/cloudflared.log | grep "https://"
```

### Перезапустить Cloudflare Tunnel
```bash
pkill cloudflared
nohup cloudflared tunnel --url http://localhost:8000 > ~/cloudflared.log 2>&1 &
sleep 5
cat ~/cloudflared.log | grep "https://"
```

## Тестирование API

### Проверка здоровья сервера
```bash
curl http://localhost:8000/health
```

### Информация о сервере
```bash
curl http://localhost:8000/
```

### Тестирование MCP endpoint
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

## Требования

- Ubuntu 20.04 или выше
- Python 3.8+
- WordPress 5.0+ с включенным REST API
- WordPress Application Password

## Безопасность

⚠️ **Важные рекомендации:**

1. **Application Password**: Всегда используйте Application Password вместо основного пароля
2. **HTTPS**: Cloudflare Tunnel автоматически предоставляет HTTPS
3. **Firewall**: Скрипт автоматически открывает порт 8000, но доступ через Cloudflare Tunnel безопаснее
4. **Права доступа**: Убедитесь, что WordPress пользователь имеет права на управление постами

## Устранение неполадок

### Сервер не запускается
```bash
# Проверьте логи
sudo journalctl -u wordpress-mcp-server -n 50

# Проверьте, занят ли порт 8000
sudo netstat -tulpn | grep 8000
```

### Cloudflare Tunnel не работает
```bash
# Проверьте логи tunnel
cat ~/cloudflared.log

# Перезапустите tunnel
pkill cloudflared
nohup cloudflared tunnel --url http://localhost:8000 > ~/cloudflared.log 2>&1 &
```

### WordPress API возвращает ошибки
1. Проверьте, что REST API включен в WordPress
2. Убедитесь, что используете правильный Application Password
3. Проверьте, что пользователь имеет права на создание постов

### ChatGPT не подключается
1. Убедитесь, что используете правильный HTTPS URL из Cloudflare Tunnel
2. URL должен заканчиваться на `/sse`
3. Проверьте, что сервер запущен: `sudo systemctl status wordpress-mcp-server`

## Структура проекта

```
wordpress-mcp-server/
├── mcp_sse_server.py      # Основной сервер
├── requirements.txt        # Python зависимости
├── install.sh             # Скрипт установки
└── README.md              # Документация
```

## Лицензия

MIT License

## Автор

Создано для работы с ChatGPT через Model Context Protocol (MCP)

## Поддержка

Если у вас возникли проблемы:
1. Проверьте логи: `sudo journalctl -u wordpress-mcp-server -f`
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурацию WordPress credentials в `mcp_sse_server.py`

## Дополнительная информация

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

