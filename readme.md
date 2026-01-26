


# 🌐 External API Interceptor & Proxy  
### with Asynchronous Object Storage

---

## 📌 Overview

This project is a **config-driven external API interceptor** built using **FastAPI**.  
It acts as a **transparent proxy** between a client and third-party APIs, forwarding requests, returning responses, and **asynchronously persisting request/response data** to **MinIO (S3-compatible object storage)** — **without increasing client-visible latency**.

The system is intentionally designed to be **simple, extensible, and production-aligned**, focusing on correct architectural decisions rather than over-engineering.

---

## 🧠 Problem Statement

In many real-world systems, we need to:

- Interact with **external APIs** safely  
- **Abstract** third-party providers from clients  
- **Archive requests and responses** for auditing, debugging, or replay  
- Do all this **without affecting client performance**

This project solves exactly that problem.

---

## 🏗️ High-Level Architecture

```

Client (A)
│
▼
Proxy / Interceptor (B)  ───▶  External API (C)
│
└──────────────▶  MinIO Object Storage

```

### Roles

- **Client (A):** Swagger UI, Postman, frontend, or any HTTP client  
- **Proxy (B):** FastAPI service (this project)  
- **External API (C):** Any third-party API (e.g. JSONPlaceholder, RapidAPI, public APIs)

> The client never communicates with the external API directly — it only talks to the proxy.

---

## ✨ Key Features

- 🔁 **Single generic proxy endpoint** for all external APIs  
- ⚙️ **Environment-driven configuration** (no hard-coded URLs)  
- 🚀 **Low client latency** using asynchronous background tasks  
- 📦 **Durable storage** of request, response, and metadata in MinIO  
- 🧩 Clean separation of concerns (proxy logic, storage, config)  
- 🧪 Easy to demo, extend, and reason about  

---

## 🔄 Request Lifecycle

1. Client sends a request to the proxy  
2. Proxy forwards the request to the external API  
3. Proxy immediately returns the response to the client  
4. Proxy asynchronously stores:
   - request payload  
   - response payload  
   - metadata (latency, timestamp, status)

> **Important:** Storage never blocks the client response.

---

## 📂 Storage Layout (MinIO)

Each intercepted API call is stored as three objects:

```

proxy-storage/
├── requests/
│   └── <request_id>.json
├── responses/
│   └── <request_id>.json
└── metadata/
└── <request_id>.json

```

Together, these represent a **complete trace of one API interaction**.

---

## 🧪 API Design

### 🔁 Generic Proxy Endpoint

```

POST /proxy/external

````

#### Request Body

```json
{
  "method": "GET",
  "path": "/posts/1",
  "query": {},
  "headers": {},
  "body": null
}
````

**Fields**

* `method` — HTTP method (GET, POST, PUT, DELETE, …)
* `path` — Path relative to the external API base URL
* `query` — Optional query parameters
* `headers` — Optional headers
* `body` — Optional JSON body

#### Response

```json
{
  "request_id": "uuid",
  "data": { },
  "latency_ms": 123
}
```

---

## ⚙️ Configuration

All configuration is externalized using environment variables.

### `.env.example`

```env
EXTERNAL_BASE_URL=https://jsonplaceholder.typicode.com

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=proxy-storage
```

> Changing the external API requires **no code changes** — only updating the environment variable.

---

## 🚀 Running the Project

### 1️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Start MinIO

```bash
docker-compose up -d
```

MinIO Console:

```
http://localhost:9001
```

### 4️⃣ Run the Proxy

```bash
uvicorn services.proxy.main:app --port 8001 --reload
```

Swagger UI:

```
http://127.0.0.1:8001/docs
```

---

## 📊 Latency Design

* **Client latency** is measured only on the synchronous request path
* **MinIO writes run asynchronously** using FastAPI background tasks
* Storage latency does **not** affect the client

This mirrors how **production API gateways** handle logging and archiving.

---

## 🧰 Utility Scripts

A `scripts/` folder contains helper scripts to extract archived data from MinIO.

Example:

```bash
python scripts/extract_all.py
```

This exports request, response, and metadata JSON files for offline analysis.

---

## ❓ Why These Design Choices?

### Why MinIO instead of a database?

* No querying required
* Handles large payloads well
* Cheap, durable object storage

### Why no Kafka / streaming?

* No real-time consumers
* Avoided unnecessary cost and complexity

### Why a single generic endpoint?

* Easier to maintain
* Highly extensible
* Mirrors real API gateway behavior

---

## 🧠 What This Project Demonstrates

* API gateway / proxy design
* External service abstraction
* Asynchronous processing
* Object storage usage
* Configuration-driven systems
* Latency-aware backend design

---

## 📌 Future Enhancements (Optional)

* Domain allow-listing
* Authentication & rate limiting
* Response caching
* Support for non-JSON payloads

---

## 👤 Author

**Yash Nigam**
Backend / Full-Stack Developer

---

## 📜 License

This project is for **learning and demonstration purposes**.

