# FastAPI JSONAPI with Supabase Example

In this example, we'll create a simple FastAPI application that adheres to the JSON:API specification using PyJAS. We'll connect the API to a Supabase PostgreSQL database to handle data storage.

## Prerequisites

- Python 3.10+
- Supabase account and project
- `pip` package manager

## Setup

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install fastapi uvicorn pyjas asyncpg sqlalchemy supabase
```

### 2. Configure Supabase

Sign up for a [Supabase](https://supabase.com/) account and create a new project. Note down the **API URL** and **API Key** from your Supabase project settings.

Create a table named `articles` with the following schema:

- `id`: UUID (Primary Key)
- `title`: Text
- `content`: Text
- `created_at`: Timestamp

### 3. Server-Side Code

Create a file named `main.py` and add the following code:

```python
from fastapi import FastAPI, HTTPException
from pyjas.v1_1 import Document, ResourceObject, JSONAPIObject
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import asyncpg
import os

# Configuration
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")  # e.g., "postgresql://user:password@host:port/dbname"

# Pydantic Models

class ArticleAttributes(BaseModel):
    title: str
    content: str

class Article(ResourceObject):
    type_: str = Field("articles", alias="type")
    id_: Optional[str] = Field(None, alias="id")
    attributes: ArticleAttributes

# Initialize FastAPI
app = FastAPI()

# Database connection pool
@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

# Create Article
@app.post("/articles", response_model=Document)
async def create_article(document: Document):
    if not isinstance(document.data, Article):
        raise HTTPException(status_code=400, detail="Invalid data")
    article: Article = document.data
    article_id = str(uuid.uuid4())
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO articles(id, title, content, created_at)
            VALUES($1, $2, $3, NOW())
            """,
            article_id,
            article.attributes.title,
            article.attributes.content
        )
    article.id_ = article_id
    return Document(data=article)

# Get Article
@app.get("/articles/{article_id}", response_model=Document)
async def get_article(article_id: str):
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, title, content FROM articles WHERE id = $1", article_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        article = Article(
            id_=row["id"],
            attributes=ArticleAttributes(title=row["title"], content=row["content"])
        )
        return Document(data=article)

# List Articles
@app.get("/articles", response_model=Document)
async def list_articles():
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, title, content FROM articles")
        articles = [
            Article(
                id_=row["id"],
                attributes=ArticleAttributes(title=row["title"], content=row["content"])
            )
            for row in rows
        ]
        return Document(data=articles)

# Update Article
@app.patch("/articles/{article_id}", response_model=Document)
async def update_article(article_id: str, document: Document):
    if not isinstance(document.data, Article):
        raise HTTPException(status_code=400, detail="Invalid data")
    article: Article = document.data
    async with app.state.pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE articles
            SET title = $1, content = $2
            WHERE id = $3
            """,
            article.attributes.title,
            article.attributes.content,
            article_id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Article not found")
    article.id_ = article_id
    return Document(data=article)

# Delete Article
@app.delete("/articles/{article_id}", response_model=Document)
async def delete_article(article_id: str):
    async with app.state.pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM articles WHERE id = $1", article_id
        )
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Article not found")
    return Document(data=None)

# JSONAPI Object
@app.get("/jsonapi", response_model=JSONAPIObject)
async def get_jsonapi():
    return JSONAPIObject()
```

### 4. Run the Server

Set the `SUPABASE_DATABASE_URL` environment variable with your Supabase PostgreSQL connection string.

```bash
export SUPABASE_DATABASE_URL="postgresql://user:password@host:port/dbname"
```

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 5. Client-Side Code

Here's an example of how to interact with the API using Python's `requests` library.

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Create an Article
def create_article(title, content):
    article = {
        "data": {
            "type": "articles",
            "attributes": {
                "title": title,
                "content": content
            }
        }
    }
    response = requests.post(f"{BASE_URL}/articles", json=article)
    return response.json()

# Get an Article
def get_article(article_id):
    response = requests.get(f"{BASE_URL}/articles/{article_id}")
    return response.json()

# List Articles
def list_articles():
    response = requests.get(f"{BASE_URL}/articles")
    return response.json()

# Update an Article
def update_article(article_id, title, content):
    article = {
        "data": {
            "type": "articles",
            "id": article_id,
            "attributes": {
                "title": title,
                "content": content
            }
        }
    }
    response = requests.patch(f"{BASE_URL}/articles/{article_id}", json=article)
    return response.json()

# Delete an Article
def delete_article(article_id):
    response = requests.delete(f"{BASE_URL}/articles/{article_id}")
    return response.json()

# Example Usage
if __name__ == "__main__":
    # Create a new article
    new_article = create_article("Hello World", "This is my first article.")
    print("Created Article:", json.dumps(new_article, indent=2))

    article_id = new_article['data']['id']

    # Get the created article
    article = get_article(article_id)
    print("Retrieved Article:", json.dumps(article, indent=2))

    # Update the article
    updated_article = update_article(article_id, "Hello World Updated", "Updated content.")
    print("Updated Article:", json.dumps(updated_article, indent=2))

    # List all articles
    articles = list_articles()
    print("All Articles:", json.dumps(articles, indent=2))

    # Delete the article
    delete_response = delete_article(article_id)
    print("Delete Response:", json.dumps(delete_response, indent=2))
```

### 6. Testing the API

You can use tools like [Postman](https://www.postman.com/) or [HTTPie](https://httpie.io/) to test the API endpoints. Below are example `curl` commands:

- **Create an Article:**

    ```bash
    curl -X POST "http://localhost:8000/articles" \
    -H "Content-Type: application/vnd.api+json" \
    -d '{
        "data": {
            "type": "articles",
            "attributes": {
                "title": "Sample Article",
                "content": "This is a sample article."
            }
        }
    }'
    ```

- **Get an Article:**

    ```bash
    curl -X GET "http://localhost:8000/articles/{article_id}" \
    -H "Accept: application/vnd.api+json"
    ```

- **List Articles:**

    ```bash
    curl -X GET "http://localhost:8000/articles" \
    -H "Accept: application/vnd.api+json"
    ```

- **Update an Article:**

    ```bash
    curl -X PATCH "http://localhost:8000/articles/{article_id}" \
    -H "Content-Type: application/vnd.api+json" \
    -d '{
        "data": {
            "type": "articles",
            "id": "{article_id}",
            "attributes": {
                "title": "Updated Title",
                "content": "Updated content."
            }
        }
    }'
    ```

- **Delete an Article:**

    ```bash
    curl -X DELETE "http://localhost:8000/articles/{article_id}" \
    -H "Accept: application/vnd.api+json"
    ```

## Conclusion

This example demonstrates how to build a JSON:API-compliant FastAPI application using PyJAS and Supabase. By following the JSON:API standards, you ensure that your API is consistent, maintainable, and easily consumable by various clients.

For more advanced usage and features, refer to the [official documentation](https://kmbhm1.github.io/PyJAS).
