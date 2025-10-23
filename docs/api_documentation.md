```markdown
# API Documentation

## **1. Authentication API**

### **POST /auth/login**
- **Описание:** Авторизация пользователя
- **Параметры запроса (JSON):**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Ответ (200 OK):**
  ```json
  {
    "access_token": "eyJhbGci...",
    "token_type": "Bearer"
  }
  ```

---

### **POST /auth/register**
- **Описание:** Регистрация нового пользователя
- **Параметры запроса (JSON):**
  ```json
  {
    "email": "newuser@example.com",
    "password": "securepassword",
    "role": "startup"
  }
  ```
- **Ответ (201 Created):**
  ```json
  {
    "message": "User registered successfully"
  }
  ```

---

## **2. Startups API**

### **POST /startups/upload**
- **Описание:** Загрузка питч-дека
- **Параметры запроса:**  
  - `file` (PDF/PPTX)
- **Ответ (200 OK):**
  ```json
  {
    "message": "Pitch deck uploaded successfully"
  }
  ```

### **POST /startups/due-diligence**
- **Описание:** Отправка заполненного чек-листа
- **Параметры запроса (JSON):**
  ```json
  {
    "market_size": "$500M-$1B",
    "traction": "High",
    "risks": "Low"
  }
  ```
- **Ответ (200 OK):**
  ```json
  {
    "message": "Due diligence submitted successfully"
  }
  ```
```

