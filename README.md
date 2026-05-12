# CS50_SQL_Final_Project_Cinema
Project databases for cinema. Using PostgresSQL and Redis.

🎬 Кинотеатр: База данных (PostgreSQL + Redis)
Полная схема базы данных для онлайн-кинотеатра с бронированием билетов, кешированием и блокировками в Redis.

```markdown
# 🎬 База данных кинотеатра: PostgreSQL + Redis

Полная структура базы данных для системы бронирования билетов в кинотеатр с использованием **PostgreSQL** в качестве основного хранилища и **Redis** для кеширования и управления блокировками.

## 📋 Содержание

- [Схема PostgreSQL](#схема-postgresql)
  - [1. movies (фильмы)](#1-movies-фильмы)
  - [2. halls (кинозалы)](#2-halls-кинозалы)
  - [3. sessions (сеансы)](#3-sessions-сеансы)
  - [4. seats (места)](#4-seats-места)
  - [5. users (пользователи)](#5-users-пользователи)
  - [6. tickets (билеты)](#6-tickets-билеты)
  - [7. payments (платежи)](#7-payments-платежи)
  - [8. genres (жанры) - опционально](#8-genres-жанры---опционально)
- [Индексы](#индексы)
- [Redis: кеширование и блокировки](#redis-кеширование-и-блокировки)
- [Триггеры](#триггеры)
- [Примеры запросов](#примеры-запросов)

---

## 🗄️ Схема PostgreSQL

### 1. `movies` (фильмы)

Хранит информацию о фильмах в прокате.

```sql
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0),
    release_date DATE,
    rating NUMERIC(3,1) CHECK (rating >= 0 AND rating <= 10),
    poster_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | Уникальный идентификатор |
| `title` | VARCHAR(255) | Название фильма |
| `description` | TEXT | Описание, режиссер, актеры |
| `duration_minutes` | INT | Продолжительность в минутах |
| `release_date` | DATE | Дата выхода в прокат |
| `rating` | NUMERIC(3,1) | Рейтинг (0-10) |
| `poster_url` | TEXT | URL постера |
| `created_at` | TIMESTAMP | Дата добавления |
| `updated_at` | TIMESTAMP | Дата обновления |

**Пример данных:**
```sql
(1, 'Оппенгеймер', 'Биографический фильм о создателе атомной бомбы', 
 180, '2023-07-20', 8.6, 'https://.../poster.jpg', 
 '2023-06-01 10:00:00', '2023-06-01 10:00:00')
```

---

### 2. `halls` (кинозалы)

Содержит информацию о физических залах кинотеатра.

```sql
CREATE TABLE halls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    rows_count INT,
    seats_per_row INT
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | Номер кинозала |
| `name` | VARCHAR(100) | Название зала |
| `capacity` | INT | Общее количество мест |
| `rows_count` | INT | Количество рядов |
| `seats_per_row` | INT | Мест в ряду |

**Пример данных:**
```sql
(1, 'Зал 1: IMAX', 250, 15, 18)
(2, 'VIP Зал', 48, 6, 8)
(3, 'Зал 3D', 180, 12, 15)
```

---

### 3. `sessions` (сеансы)

Определяет время и место показа фильмов.

```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    hall_id INT REFERENCES halls(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(hall_id, start_time)
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | Идентификатор сеанса |
| `movie_id` | INT | Какой фильм (FK → movies) |
| `hall_id` | INT | В каком зале (FK → halls) |
| `start_time` | TIMESTAMP | Начало сеанса |
| `end_time` | TIMESTAMP | Конец сеанса |
| `price` | DECIMAL(10,2) | Базовая цена билета |
| `created_at` | TIMESTAMP | Дата создания |

**Пример данных:**
```sql
(1, 1, 1, '2024-03-20 19:00:00', '2024-03-20 22:00:00', 450.00, '2024-03-01 09:00:00')
```

---

### 4. `seats` (места)

Физическая схема мест каждого зала.

```sql
CREATE TABLE seats (
    id SERIAL PRIMARY KEY,
    hall_id INT REFERENCES halls(id) ON DELETE CASCADE,
    row_num INT NOT NULL,
    seat_num INT NOT NULL,
    seat_type VARCHAR(50) DEFAULT 'standard',
    UNIQUE(hall_id, row_num, seat_num)
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | Уникальный ID места |
| `hall_id` | INT | FK → halls |
| `row_num` | INT | Номер ряда |
| `seat_num` | INT | Номер места в ряду |
| `seat_type` | VARCHAR(50) | Тип: 'standard', 'vip', 'disabled' |

**Пример данных (VIP зал):**
```sql
(1, 2, 1, 1, 'vip')
(2, 2, 1, 2, 'vip')
(3, 2, 1, 3, 'standard')
```

---

### 5. `users` (пользователи)

Регистрационные данные пользователей.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'customer',
    registered_at TIMESTAMP DEFAULT NOW()
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | ID пользователя |
| `email` | VARCHAR(255) | Email для входа |
| `phone` | VARCHAR(20) | Номер телефона |
| `first_name` | VARCHAR(100) | Имя |
| `last_name` | VARCHAR(100) | Фамилия |
| `password_hash` | TEXT | Хеш пароля |
| `role` | VARCHAR(50) | 'customer', 'manager', 'admin' |
| `registered_at` | TIMESTAMP | Дата регистрации |

**Пример данных:**
```sql
(1, 'ivan@example.com', '+79991234567', 'Иван', 'Петров', 
 '$2y$10$...', 'customer', '2024-01-15 14:30:00')
```

---

### 6. `tickets` (билеты)

Центральная таблица бронирования и продажи.

```sql
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id) ON DELETE CASCADE,
    seat_id INT REFERENCES seats(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    booking_code UUID DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL DEFAULT 'available',
    price DECIMAL(10,2) NOT NULL,
    booked_at TIMESTAMP,
    paid_at TIMESTAMP,
    UNIQUE(session_id, seat_id)
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | Номер билета |
| `session_id` | INT | FK → sessions |
| `seat_id` | INT | FK → seats |
| `user_id` | INT | FK → users (NULL если гость) |
| `booking_code` | UUID | Уникальный код бронирования |
| `status` | VARCHAR(50) | 'available', 'reserved', 'sold', 'cancelled' |
| `price` | DECIMAL(10,2) | Цена на момент покупки |
| `booked_at` | TIMESTAMP | Время резервирования |
| `paid_at` | TIMESTAMP | Время оплаты |

**Пример данных:**
```sql
-- Проданный билет
(1001, 1, 15, 42, '550e8400-e29b-41d4-a716-446655440000', 
 'sold', 450.00, '2024-03-15 10:00:00', '2024-03-15 10:05:00')

-- Забронированный
(1002, 1, 16, 42, '550e8400-e29b-41d4-a716-446655440001', 
 'reserved', 450.00, '2024-03-15 10:00:00', NULL)
```

---

### 7. `payments` (платежи)

Финансовые транзакции по билетам.

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | ID платежа |
| `ticket_id` | INT | FK → tickets |
| `amount` | DECIMAL(10,2) | Сумма платежа |
| `payment_method` | VARCHAR(50) | 'card', 'cash', 'online' |
| `status` | VARCHAR(50) | 'pending', 'completed', 'failed', 'refunded' |
| `transaction_id` | VARCHAR(255) | ID в платежной системе |
| `created_at` | TIMESTAMP | Время создания |

**Пример данных:**
```sql
(1, 1001, 450.00, 'card', 'completed', 'tr_20240315_123456', '2024-03-15 10:05:00')
```

---

### 8. `genres` (жанры) - опционально

Связь многие-ко-многим с фильмами.

```sql
CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE movie_genres (
    movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INT REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);
```

**Пример данных:**
```sql
-- Жанры
(1, 'Боевик'), (2, 'Драма'), (3, 'Комедия'), (4, 'Фантастика')

-- Связи
(1, 2) -- Оппенгеймер + Драма
(1, 4) -- Оппенгеймер + Фантастика
```

---

## 📊 Индексы

```sql
-- Для быстрого поиска сеансов
CREATE INDEX idx_sessions_start_time ON sessions(start_time);
CREATE INDEX idx_sessions_movie_id ON sessions(movie_id);

-- Для работы с билетами
CREATE INDEX idx_tickets_session_status ON tickets(session_id, status);
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
```

---

## ⚡ Redis: кеширование и блокировки

### Структуры данных в Redis

| Ключ | Тип | TTL | Назначение |
|------|-----|-----|------------|
| `movie:{id}` | Hash | 1 час | Данные фильма |
| `session:{id}:seats` | Hash | 10 мин | Актуальная схема мест с блокировками |
| `hall:{id}:layout` | JSON | 1 день | Схема зала |
| `upcoming_movies` | List | 30 мин | Список ближайших сеансов |

### Управление блокировками мест

```redis
# Временная блокировка места (10 минут)
SET lock:session:123:seat:45 "user:456" EX 600 NX

# Активные сеансы пользователя
SADD user:456:active_sessions 123
EXPIRE user:456:active_sessions 3600

# Очередь на оплату
LPENDING payment_queue "ticket_id=789&user_id=456"
```

### Lua-скрипт для атомарного занятия места

```lua
if redis.call("SETNX", "lock:session:"..session_id..":seat:"..seat_id, user_id) == 1 then
    redis.call("EXPIRE", "lock:session:"..session_id..":seat:"..seat_id, 600)
    return 1
else
    return 0
end
```

### Пример кеширования в Python

```python
def get_today_sessions():
    # Пытаемся получить из кеша
    cached = redis.get("sessions:today")
    if cached:
        return json.loads(cached)
    
    # Запрос в PostgreSQL
    sessions = db.query(
        "SELECT * FROM sessions WHERE DATE(start_time) = CURRENT_DATE"
    )
    
    # Сохраняем в кеш на 5 минут
    redis.setex("sessions:today", 300, json.dumps(sessions))
    return sessions

def get_available_seats(session_id):
    # Проданные и забронированные места
    sold = db.query(
        "SELECT seat_id FROM tickets WHERE session_id=:sid AND status IN ('reserved','sold')",
        {"sid": session_id}
    )
    
    # Заблокированные в Redis
    locked = redis.keys(f"lock:session:{session_id}:seat:*")
    
    # Доступные места
    available = all_seats - set(sold) - set(locked)
    return available
```

---

## 🔄 Триггеры

### Автоматический расчет end_time

```sql
CREATE OR REPLACE FUNCTION calculate_end_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.end_time := NEW.start_time + 
                    (SELECT duration_minutes + 20 FROM movies WHERE id = NEW.movie_id) * INTERVAL '1 minute';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calc_end_time
    BEFORE INSERT OR UPDATE OF start_time, movie_id ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION calculate_end_time();
```

### Обновление updated_at

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_movies_updated_at
    BEFORE UPDATE ON movies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

---

## 📝 Примеры запросов

### Список сеансов на сегодня с информацией о фильмах

```sql
SELECT 
    s.id,
    m.title,
    h.name as hall_name,
    s.start_time,
    s.end_time,
    s.price,
    (h.capacity - COUNT(t.id)) as available_seats
FROM sessions s
JOIN movies m ON s.movie_id = m.id
JOIN halls h ON s.hall_id = h.id
LEFT JOIN tickets t ON t.session_id = s.id AND t.status IN ('sold', 'reserved')
WHERE DATE(s.start_time) = CURRENT_DATE
GROUP BY s.id, m.title, h.name, h.capacity, s.start_time, s.end_time, s.price
ORDER BY s.start_time;
```

### История покупок пользователя

```sql
SELECT 
    t.booking_code,
    m.title,
    h.name as hall,
    s.start_time,
    t.price,
    t.paid_at,
    t.status
FROM tickets t
JOIN sessions s ON t.session_id = s.id
JOIN movies m ON s.movie_id = m.id
JOIN halls h ON s.hall_id = h.id
WHERE t.user_id = 42 AND t.status = 'sold'
ORDER BY t.paid_at DESC;
```

### Отчет по платежам за день

```sql
SELECT 
    DATE(p.created_at) as payment_date,
    COUNT(p.id) as transactions_count,
    SUM(p.amount) as total_amount,
    p.payment_method
FROM payments p
WHERE p.status = 'completed'
  AND DATE(p.created_at) = CURRENT_DATE
GROUP BY DATE(p.created_at), p.payment_method;
```

---

## 🔗 Связи между таблицами (ER-диаграмма)

```
movies ──┬── sessions ──┬── tickets ──┬── payments
         │               │              │
         └── movie_genres┤              │
                         │              │
halls ────── sessions ───┤              │
                         │              │
seats ────── tickets ────┘              │
                                        │
users ────── tickets ───────────────────┘
```

**Кардинальность:**
- `movies` → `sessions`: один ко многим
- `halls` → `sessions`: один ко многим
- `halls` → `seats`: один ко многим
- `sessions` → `tickets`: один ко многим
- `seats` → `tickets`: один ко многим
- `users` → `tickets`: один ко многим
- `tickets` → `payments`: один к одному

---

## 🚀 Производительность и масштабирование

### Почему такая архитектура?

| Компонент | Роль | Преимущества |
|-----------|------|--------------|
| **PostgreSQL** | Постоянное хранилище | ACID, целостность данных, сложные запросы |
| **Redis** | Кеш + блокировки | Миллисекундные ответы, атомарные операции |

### Сценарий покупки билета

1. **Выбор места** → блокировка в Redis (10 минут)
2. **Подтверждение** → запись в PostgreSQL (status = 'reserved')
3. **Оплата** → обновление статуса на 'sold' + запись в payments
4. **Таймаут** → Redis-блокировка снимается автоматически

Это гарантирует, что **два пользователя не купят одно место** даже при высоких нагрузках.

---

## 📦 Установка и настройка

```bash
# PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE cinema;"
psql -d cinema -f schema.sql

# Redis
redis-server --port 6379

# Индексы (для больших объемов данных)
psql -d cinema -f indexes.sql
```

---

## 📄 Лицензия

MIT

---

## 👥 Авторы

Ваше Имя - [GitHub профиль]

---

## ⭐ Поддержка

Если этот проект помог вам, поставьте звезду на GitHub!
```

Этот Markdown-документ полностью готов для публикации на GitHub. Он включает:

- ✅ Полное описание всех таблиц с полями
- ✅ SQL-код для создания таблиц
- ✅ Примеры данных
- ✅ Индексы и триггеры
- ✅ Интеграцию с Redis
- ✅ Примеры запросов
- ✅ ER-диаграмму текстом
- ✅ Сценарии использования
- ✅ Инструкцию по установке
