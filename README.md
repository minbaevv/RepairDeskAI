# RepairDesk AI

Учебный AI-помощник сервисного центра. Без регистрации и фронтенда: запросы отправляются через Swagger или HTTP.

## Запуск в Windows PowerShell

Используйте Python 3.11 или 3.12. Откройте терминал в корне проекта.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item mysite/.env.example mysite/.env
```

Впишите свой ключ в `mysite/.env`. Ключ нельзя публиковать. Модель по умолчанию `openai/gpt-4o-mini` платная; расходы зависят от OpenRouter. Можно выбрать другую модель с поддержкой tool calling. Бесплатные модели не гарантируют поддержку инструментов и структурированного вывода.

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn mysite.main:app --reload --host 127.0.0.1
```

Swagger: http://127.0.0.1:8000/docs

SQLite-файл `repair.db` создаётся миграцией в корне проекта. Папка `admin` оставлена для соответствия твоей структуре, админ-панель не реализована.

При первом старте embeddings скачиваются с Hugging Face: нужны интернет, место на диске и время. База знаний индексируется заново при запуске и хранится в памяти. `/health` показывает готовность AI-компонентов; доступность удалённой модели проверяется только при реальном запросе. Если нет API-ключа или RAG не загрузился, обычные CRUD-эндпоинты продолжают работать после миграции.

## Структура

```text
RepairDeskAI/
├── migrations/
│   ├── versions/0001_create_requests.py
│   ├── env.py
│   └── script.py.mako
├── mysite/
│   ├── admin/
│   ├── api/
│   │   ├── chat.py
│   │   └── repair.py
│   ├── chain/
│   │   ├── agent.py
│   │   ├── model.py
│   │   ├── rag.py
│   │   ├── tools.py
│   │   ├── validation.py
│   │   └── repair_knowledge.txt
│   ├── database/
│   │   ├── db.py
│   │   ├── models.py
│   │   └── services.py
│   ├── schemas/
│   │   ├── chat.py
│   │   └── repair.py
│   ├── .env.example
│   ├── config.py
│   └── main.py
├── tests/test_validation.py
├── alembic.ini
├── README.md
└── requirements.txt
```

Пакеты содержат пустые `__init__.py`.

## Три RunnableLambda

`normalize_text` убирает лишние пробелы и нормализует Unicode.

`check_length` проверяет, что сообщение содержит не более 200 слов и 3000 символов.

`check_blocked_words` блокирует заданные слова и несколько словоформ.

`input_chain = RunnableLambda(normalize_text) | RunnableLambda(check_length) | RunnableLambda(check_blocked_words)` — LCEL-цепочка типа RunnableSequence.

Фильтр слов — учебная проверка, а не полноценная модерация: возможны обходы и ложные срабатывания. Он применяется до вызова модели, а также к текстовым аргументам инструментов и REST-запросов.

## RAG и JSON

`TextLoader → Documents → RecursiveCharacterTextSplitter → HuggingFaceEmbeddings → InMemoryVectorStore → similarity_search → ChatPromptTemplate → model.with_structured_output(KnowledgeAnswer)`.

`with_structured_output()` возвращает Pydantic-объект, а FastAPI сериализует его в настоящий JSON, не строку с Markdown-ограждениями. Используется `method="function_calling"`; выбранная модель должна поддерживать инструменты. Фрагменты и векторная похожесть не гарантируют, что модель всегда правильно определит отсутствие ответа.

Запрос `POST /ask`:

```json
{"message": "Сколько стоит диагностика?"}
```

Ожидаемая форма ответа:

```json
{"answer": "Диагностика стоит 500 сом. При согласии на ремонт она бесплатна.", "sources": ["repair_knowledge.txt"]}
```

Данные сервисного центра вымышлены. `sources` показывает имя использованного файла, а не подтверждённую ссылку на каждый факт ответа.

## Агент: ровно три инструмента

- `request_create`: создание заявки.
- `request_update`: изменение статуса или проблемы по id.
- `request_list`: список с фильтром, пагинацией и общим количеством.

`create_agent()` организует цикл «модель → вызов инструмента → ToolMessage → модель». Не нужно дополнительно вручную вызывать `bind_tools()` для того же агента.

Каждый `POST /agent` — независимый запрос без памяти. При уточнении передавайте полный запрос заново. Имена клиентов в примерах вымышлены. Для обновления используйте реальный id из ответа создания или списка.

```json
{"message": "Создай заявку: клиент Айбек, устройство Lenovo IdeaPad, проблема — не включается"}
```

```json
{"message": "Обнови заявку 1: статус in_progress"}
```

```json
{"message": "Покажи все заявки со статусом in_progress"}
```

Форма ответа агента:

```json
{
  "answer": "Заявка создана.",
  "results": [
    {
      "tool": "request_create",
      "result": {
        "ok": true,
        "request": {
          "id": 1,
          "client_name": "Айбек",
          "device": "Lenovo IdeaPad",
          "problem": "не включается",
          "status": "new",
          "created_at": "2026-01-01T10:00:00Z"
        }
      }
    }
  ]
}
```

`results` формируется из фактических ToolMessage, а не выдумывается моделью. Текст `answer` берётся из последнего сообщения через `StrOutputParser`. Здесь JSON задаёт Pydantic-модель FastAPI, а `with_structured_output()` используется в RAG-цепочке. `/ask` не вызывает инструменты, `/agent` не ищет в базе знаний.

## Обычный backend

- `POST /requests`: `{"client_name":"Айбек","device":"Lenovo","problem":"Не включается"}`.
- `PATCH /requests/1`: `{"status":"done"}`.
- `GET /requests?limit=20&offset=0`: список.
- `GET /requests?status=new`: фильтр.

Статусы: `new`, `in_progress`, `done`, `cancelled`.

## Тесты

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Тесты покрывают три функции проверки входного текста без запросов к AI. Интеграционная работа OpenRouter и загрузка embeddings требуют отдельного запуска с ключом и интернетом. Версии зависимостей ограничены диапазонами, но не зафиксированы lock-файлом.

## Из твоего списка

В основном проекте используются HumanMessage, ToolMessage, ответы модели AIMessage внутри агента, ChatPromptTemplate, StrOutputParser, LCEL, RunnableLambda, RunnableSequence, ainvoke, Pydantic, with_structured_output, @tool, tool calling, create_agent, Documents, loaders, splitters, embeddings, vector stores и similarity search.

SystemMessage создаётся внутри шаблона и агента. temperature и max_tokens настраиваются в config.py. AIMessageChunk, streaming, batch, RunnableParallel, RunnablePassthrough и ручной agent loop не добавлены, чтобы базовый проект не был перегружен. `top_k` и `num_predict` зависят от провайдера и не являются универсальными параметрами ChatOpenAI; `num_predict` обычно относится к Ollama. Context window — ограничение модели, а не команда.

## Ограничения

Это локальный однопользовательский учебный проект. Нет авторизации, разграничения доступа, защиты от повторного создания одной заявки, истории диалогов, подтверждения изменений или защиты от всех prompt injection. Не публикуйте сервер в интернете в таком виде. Любой имеющий доступ к API может просматривать и изменять заявки. При ошибке после выполнения инструмента запись могла уже сохраниться: перед повтором проверьте список.
