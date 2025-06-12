**URL Shortener Project Tracker**

---

### ✅ Completed Enhancements

1. **Unit Testing with pytest**

   - Pytest fixtures adapted for SQLite test database.
   - Test cases for basic shortening and resolution.
   - Expiration logic tested with future and past timestamps.

2. **/stats Endpoint**

   - Route `/stats` shows total number of URLs and optionally breakdown by active/expired.
   - Manually tested with curl and Postman.

3. **Improved Manual Testing**

   - Postman collection created with working tests for:
     - /shorten
     - /resolve
     - /list
     - /stats

4. **Switch to SQLite using SQLAlchemy**

   - `model/models.py` contains `URLMap` class.
   - `model/db.py` manages engine and session.
   - `shortener.py` refactored to use SQLAlchemy instead of JSON.
   - Tests updated to use SQLite with temp file fixture.

---

### 🛠️ Upcoming Enhancements

5. **Minimal Web UI** (Next task)

   - HTML form for input
   - Output display for shortened or resolved URL
   - Optionally support expiration setting

6. **Deployment**

   - Prepare project for deployment on platforms like Render/Heroku
   - Configurable database path
   - Use production-ready WSGI server (e.g., Gunicorn)

7. **Rate Limiting / API Key Support**

   - Add API key requirement for usage
   - Optional rate limiting per key

8. **Custom Short Codes**

   - Allow client to specify desired short code (if available)

9. **QR Code Generation**

   - Return QR code image or link with shortened URL

---

### 📁 Project Structure (as of now)

```
project_root/
│
├── app.py
├── shortener.py
├── tests/
│   └── test_shortener.py
├── model/
│   ├── __init__.py
│   ├── models.py
│   └── db.py
└── requirements.txt
```

---

Let me know when you're ready to start with the Minimal Web UI.

