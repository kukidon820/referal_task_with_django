# Тестовое задание ссылка - https://kukidon.pythonanywhere.com/ref/


Все зависимости описаны в файле `requirements.txt`.


1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/kukidon820/referal_task_with_django.git
    cd <папка-с-проектом>
    ```

2.  **Запустите приложение с помощью Docker Compose:**
    ```bash
    docker-compose up --build
    ```

3.  **Выполните миграции (если контейнер уже запущен):**
    В новом терминале:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4.  **(Опционально) Создайте суперпользователя:**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

5.  **Доступ:**
    *   Главная страница (HTML): `http://localhost:8000/ref/`
    *   API: `http://localhost:8000/ref/api/`
    *   Документация Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
    *   Документация ReDoc: `http://localhost:8000/api/schema/redoc/`
    *   Админка Django: `http://localhost:8000/admin/` (после создания суперпользователя)

## API Endpoints

### 1. Пользователи (CRUD)
*   **URL:** `GET|POST /ref/api/users/`
*   **URL:** `GET|PUT|DELETE /ref/api/users/{id}/`
*   Позволяет выполнять все операции создания, чтения, обновления и удаления пользователей.

### 2. Коды авторизации (CRUD)
*   **URL:** `GET|POST /ref/api/auth-codes/`
*   **URL:** `GET|PUT|DELETE /ref/api/auth-codes/{id}/`
*   Позволяет управлять кодами авторизации.

### 3. Отправка кода авторизации
*   **URL:** `POST /ref/api/send-code/`
*   **Тело запроса:**
    ```json
    {
      "phone_number": "+375299876751"
    }
    ```
*   **Ответ:**
    ```json
    {
      "message": "Код отправлен на номер +375299876751",
      "user_id": 1
    }
    ```

### 4. Проверка кода авторизации
*   **URL:** `POST /ref/api/verify-code/`
*   **Тело запроса:**
    ```json
    {
      "phone_number": "+375299876751",
      "code": "1234"
    }
    ```
*   **Ответ (успех):**
    ```json
    {
      "message": "Успешный вход!",
      "user_id": 1
    }
    ```
*   **Ответ (ошибка):**
    ```json
    {
      "error": "Неверный или уже использованный код."
    }
    ```

### 5. Получение профиля пользователя
*   **URL:** `GET /ref/api/profile/`
*   **Требуется аутентификация (токен или сессия).**
*   **Ответ:**
    ```json
    {
      "phone_number": "+375299876751",
      "invite_code": "A1B2C3",
      "activated_invite_code": "X9Y8Z7",
      "invited_users": ["+375299876751", "+375299876753"]
    }
    ```

### 6. Активация инвайт-кода
*   **URL:** `POST /ref/api/activate-invite/`
*   **Требуется аутентификация (токен или сессия).**
*   **Тело запроса:**
    ```json
    {
      "invite_code": "X9Y8Z7"
    }
    ```
*   **Ответ (успех):**
    ```json
    {
      "message": "Успешная активация кода приглашения!"
    }
    ```
*   **Ответ (ошибка):**
    ```json
    {
      "error": "Вы уже ввели код приглашения."
    }
    ```
