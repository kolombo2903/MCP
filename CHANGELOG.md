# Changelog

Все заметные изменения в проекте будут документированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-04

### Added
- Начальный релиз WordPress MCP Server
- Поддержка Model Context Protocol (MCP) через SSE
- 4 основных инструмента:
  - `create_post` - создание постов в WordPress
  - `update_post` - обновление существующих постов
  - `get_posts` - получение списка постов
  - `delete_post` - удаление постов
- FastAPI сервер с поддержкой SSE
- Интеграция с WordPress REST API
- Автоматический скрипт установки для Ubuntu
- Поддержка Cloudflare Tunnel для HTTPS
- Systemd сервис для автозапуска
- Полное логирование всех операций
- Health check endpoint
- CORS поддержка для ChatGPT
- Асинхронная обработка запросов
- Обработка ошибок и валидация
- Документация на русском языке

### Features
- JSON-RPC 2.0 протокол для MCP
- Server-Sent Events (SSE) для real-time связи
- Basic Authentication для WordPress API
- Heartbeat механизм для поддержания соединения
- Configurable post status (publish/draft/private)
- Pagination для списка постов

### Documentation
- Подробный README с инструкциями
- Примеры использования всех инструментов
- Руководство по установке и настройке
- Troubleshooting секция
- Рекомендации по безопасности

[1.0.0]: https://github.com/yourusername/wordpress-mcp-server/releases/tag/v1.0.0

