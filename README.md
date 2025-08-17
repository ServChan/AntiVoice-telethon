# 📖 README для AntiVoice-Telethon

## Описание
AntiVoice-Telethon — это Telegram-скрипт на основе Telethon, который автоматически фильтрует голосовые сообщения. Он может:
- предупреждать и удалять короткие войсы,
- работать в разных режимах (только предупреждать, только удалять, выключен),
- управляться командами в личке,
- хранить настройки в JSON без правки кода.

## Установка
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ServChan/AntiVoice-telethon.git
   cd AntiVoice-telethon
   ```
2. Установите зависимости:
   ```bash
   pip install telethon colorama
   ```
3. Создайте файл конфигурации `config.json` (см. пример ниже). Минимально укажите `api_id`, `api_hash`, `session` и `phone`.
4. Запустите скрипт:
   ```bash
   python stopvoice.py
   ```

## Пример `config.json`
```json
{
  "api_id": 123456,
  "api_hash": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "session": "stopvoice_session",
  "phone": "+37100000000",
  "owner_ids": [123456789],
  "whitelist_ids": [],
  "whitelist_usernames": [],
  "max_duration": 10,
  "reply_text": "__Пользователь ограничил функцию голосовых сообщений.__",
  "mode": "warn_then_delete",
  "private_only": true,
  "enable": true
}
```

### Параметры
- `api_id`/`api_hash` — ключи из https://my.telegram.org
- `session` — имя файла сессии
- `phone` — номер Telegram
- `owner_ids` — ID владельцев, кто может управлять ботом
- `whitelist_ids`/`whitelist_usernames` — список исключений
- `max_duration` — порог длительности voice в секундах (меньше — будет обработано)
- `reply_text` — текст ответа при срабатывании
- `mode` — `warn_then_delete` | `warn_only` | `delete_only` | `off`
- `private_only` — работать только в личных чатах
- `enable` — глобальное включение/выключение

## Команды (только для владельцев из `owner_ids`)
Все команды отправляются в личные сообщения:
- `/allow @username|id` — добавить в белый список
- `/deny @username|id` — удалить из белого списка
- `/set <сек>` — установить порог длительности
- `/mode <режим>` — выбрать режим (`warn_then_delete|warn_only|delete_only|off`)
- `/status` — показать текущие настройки
- `/reload` — перечитать конфиг из файла
- `/enable` / `/disable` — включить/выключить фильтр
- `/wl` — показать текущий whitelist

## Примеры
- Режим `warn_then_delete`: голосовое < `max_duration` — бот отвечает `reply_text` и удаляет сообщение.
- `/allow @user`: добавить пользователя в исключения без правки кода.
- `STOPVOICE_CONFIG=/path/to/config.json python stopvoice.py`: запуск с альтернативным конфигом.

## Важно
- В группах удаление требует прав администратора у аккаунта.
- Telegram может не разрешить удаление у обоих участников в личке.
- Голос, присланный как обычный `audio` без флага `voice`, не обрабатывается.
