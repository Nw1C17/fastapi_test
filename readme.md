## README.md


Асинхронное REST API для управления балансом кошельков.  
Реализовано в рамках тестового задания (Python Developer).  
Позволяет создавать кошельки, пополнять и списывать средства, получать текущий баланс.  
```
## Стек технологий

- **Python 3.11**
- **FastAPI** – веб-фреймворк
- **PostgreSQL** – база данных
- **SQLAlchemy 2.0** (async) – ORM
- **Alembic** – миграции
- **Docker / Docker Compose** – контейнеризация
- **Pytest** – тестирование
```
## Возможности

- Создание кошелька (`POST /api/v1/wallets/`)
- Пополнение баланса (`DEPOSIT`)
- Списание баланса (`WITHDRAW`) с проверкой достаточности средств
- Получение баланса (`GET /api/v1/wallets/{uuid}`)
- Автоматические миграции БД
- Конкурентная безопасность (блокировка строк PostgreSQL `SELECT ... FOR UPDATE`)
- Полное покрытие тестами (включая тест на параллельные запросы)


### Запуск (Docker)

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Nw1C17/fastapi_test.git
```

### 2. Запустить контейнеры
```bash
docker-compose up --build
```

При первом запуске автоматически:
- создадутся миграции
- будет создана таблица `wallets`
- запустится сервер на `http://localhost:8000`

### 3. Проверить работу
Откройте интерактивную документацию:  
[http://localhost:8000/docs](http://localhost:8000/docs)

## Примеры запросов

### Создание кошелька
```http
POST /api/v1/wallets/
```
Ответ:
```json
{
  "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### Пополнение баланса
```http
POST /api/v1/wallets/3fa85f64-5717-4562-b3fc-2c963f66afa6/operation
Content-Type: application/json

{
  "operation_type": "DEPOSIT",
  "amount": 1000
}
```
Ответ:
```json
{
  "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": 1000
}
```

### Списание
```http
POST /api/v1/wallets/{uuid}/operation
{
  "operation_type": "WITHDRAW",
  "amount": 300
}
```

### Получение баланса
```http
GET /api/v1/wallets/{uuid}
```
Ответ:
```json
{
  "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": 700
}
```

## Тестирование

Запуск тестов (локально, при активном Docker-контейнере с БД):
```bash
pip install -r requirements.txt
docker-compose exec -e TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/wallet_db" app pytest tests/ -v
```

Тесты покрывают:
- создание кошелька
- пополнение, списание (успешное и с ошибкой при недостатке средств)
- получение баланса
- обработку несуществующего кошелька (404)
- **конкурентность**: 10 одновременных списаний с одного кошелька – финальный баланс корректен

## Архитектура и конкурентность

Для обеспечения атомарности операций и защиты от гонок при параллельных запросах к одному кошельку используется механизм блокировки строк SQLAlchemy:

```python
result = await db.execute(
    select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
)
```

В PostgreSQL `SELECT ... FOR UPDATE` блокирует строку до завершения транзакции, поэтому второй запрос будет ждать и работать с актуальным балансом.

## Структура проекта

```
.
├── app
│   ├── config.py          # переменные окружения
│   ├── database.py        # engine, AsyncSessionLocal, get_db
│   ├── models.py          # модель Wallet (SQLAlchemy)
│   ├── schemas.py         # Pydantic-схемы
│   ├── crud.py            # CRUD-операции с блокировкой
│   ├── routers
│   │   └── wallets.py     # эндпоинты
│   └── main.py            # FastAPI приложение
├── alembic                # миграции
├── tests
│   ├── test_wallets.py    # функциональные тесты
│   └── test_concurrency.py # тест на параллельные запросы
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh          # инициализация миграций и запуск
├── requirements.txt
└── README.md
```

