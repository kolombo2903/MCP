# 📤 Как опубликовать проект на GitHub

## Быстрый способ (рекомендуется)

### Вариант 1: Через скрипт автоматизации

```bash
chmod +x setup_github.sh
./setup_github.sh
```

Скрипт автоматически:
- ✅ Инициализирует Git репозиторий
- ✅ Настроит Git конфигурацию
- ✅ Добавит все файлы
- ✅ Создаст первый коммит
- ✅ Выдаст инструкции для публикации

---

## Ручной способ

### Шаг 1: Инициализация Git

```bash
cd "C:\Users\79259\Desktop\mcp video"
git init
```

### Шаг 2: Настройка Git (если не настроен)

```bash
git config user.name "Ваше Имя"
git config user.email "your.email@example.com"
```

### Шаг 3: Добавление файлов

```bash
git add .
```

### Шаг 4: Первый коммит

```bash
git commit -m "Initial commit: WordPress MCP Server v1.0.0"
```

### Шаг 5: Создание репозитория на GitHub

1. Откройте https://github.com/new
2. Заполните:
   - **Repository name**: `wordpress-mcp-server`
   - **Description**: "MCP (Model Context Protocol) server for managing WordPress posts through ChatGPT"
   - **Visibility**: Public (или Private)
3. **НЕ добавляйте** README, .gitignore или LICENSE (они уже есть)
4. Нажмите **Create repository**

### Шаг 6: Подключение к GitHub

После создания репозитория GitHub покажет команды. Выполните:

#### Через HTTPS:
```bash
git remote add origin https://github.com/ВАШ_USERNAME/wordpress-mcp-server.git
git branch -M main
git push -u origin main
```

#### Через SSH (если настроен):
```bash
git remote add origin git@github.com:ВАШ_USERNAME/wordpress-mcp-server.git
git branch -M main
git push -u origin main
```

---

## После публикации

### Обновление README на GitHub

Замените в README.md все `yourusername` на ваш реальный GitHub username:

```bash
# Найти и заменить
sed -i 's/yourusername/ВАШ_USERNAME/g' README.md
git add README.md
git commit -m "Update GitHub username in documentation"
git push
```

### Добавление Topics на GitHub

На странице репозитория добавьте topics:
- `wordpress`
- `mcp`
- `chatgpt`
- `fastapi`
- `python`
- `rest-api`
- `model-context-protocol`
- `sse`
- `cloudflare-tunnel`

### Создание Release

1. Перейдите на вкладку **Releases**
2. Нажмите **Create a new release**
3. Заполните:
   - **Tag**: `v1.0.0`
   - **Title**: `WordPress MCP Server v1.0.0`
   - **Description**: Скопируйте из CHANGELOG.md
4. Нажмите **Publish release**

---

## Дальнейшие обновления

### Внесение изменений

```bash
# Внесите изменения в файлы

# Добавьте изменения
git add .

# Создайте коммит
git commit -m "Описание изменений"

# Отправьте на GitHub
git push
```

### Создание новой версии

```bash
# Обновите CHANGELOG.md с новыми изменениями

# Создайте коммит
git add CHANGELOG.md
git commit -m "Release v1.1.0"

# Создайте тег
git tag -a v1.1.0 -m "Version 1.1.0"

# Отправьте коммиты и теги
git push
git push --tags
```

---

## Полезные команды Git

```bash
# Проверка статуса
git status

# Просмотр истории
git log --oneline

# Просмотр изменений
git diff

# Отмена изменений (до коммита)
git checkout -- filename

# Просмотр удалённых репозиториев
git remote -v

# Клонирование репозитория
git clone https://github.com/USERNAME/wordpress-mcp-server.git
```

---

## Структура проекта на GitHub

```
wordpress-mcp-server/
├── .gitignore              # Игнорируемые файлы
├── LICENSE                 # MIT лицензия
├── README.md               # Главная документация
├── CHANGELOG.md            # История изменений
├── CONTRIBUTING.md         # Руководство для контрибьюторов
├── PUBLISH_GITHUB.md       # Эта инструкция
├── mcp_sse_server.py       # Основной сервер
├── requirements.txt        # Python зависимости
├── install.sh              # Скрипт установки
├── setup_github.sh         # Скрипт для GitHub
└── config.example.py       # Пример конфигурации
```

---

## Безопасность

⚠️ **ВАЖНО**: Никогда не публикуйте на GitHub:
- Реальные пароли WordPress
- Application passwords
- Файлы конфигурации с чувствительными данными
- Файл `.env` (он в .gitignore)

Файл `mcp_sse_server.py` содержит placeholder значения:
```python
WORDPRESS_URL = "https://your-wordpress-site.com/"
WORDPRESS_USERNAME = "your-username"
WORDPRESS_PASSWORD = "your-password"
```

Пользователи должны заменить их своими данными после клонирования.

---

## Готово! 🎉

Ваш проект теперь на GitHub:
`https://github.com/ВАШ_USERNAME/wordpress-mcp-server`

Поделитесь ссылкой с сообществом! 🚀

