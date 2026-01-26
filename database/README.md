# Database Setup Guide

This chatbot application uses MySQL with SQLAlchemy ORM for storing conversation threads, checkpoints, and document metadata.

## Technology Stack

- **Database**: MySQL 5.7+ or MySQL 8.0+
- **ORM**: SQLAlchemy 2.x
- **Driver**: PyMySQL
- **Features**: Connection pooling, automatic migrations, ORM models

## Database Schema

The application uses the following tables (defined as SQLAlchemy ORM models):

### 1. thread_metadata
Stores thread titles and metadata for chat conversations.
- `thread_id` (VARCHAR 255, PRIMARY KEY): Unique identifier for each conversation thread
- `title` (VARCHAR 255): Display title for the thread
- `created_at` (TIMESTAMP): When the thread was created
- `updated_at` (TIMESTAMP): Last update timestamp

### 2. document_metadata
Stores information about uploaded documents per thread.
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY): Unique document ID
- `thread_id` (VARCHAR 255, FOREIGN KEY): Associated thread
- `filename` (VARCHAR 500): Original filename
- `documents_count` (INT): Number of documents in the PDF
- `chunks_count` (INT): Number of text chunks created
- `uploaded_at` (TIMESTAMP): Upload timestamp

### 3. checkpoints
LangGraph checkpoint storage for conversation state.
- `thread_id` (VARCHAR 255): Thread identifier
- `checkpoint_ns` (VARCHAR 255): Checkpoint namespace
- `checkpoint_id` (VARCHAR 255): Checkpoint identifier
- `parent_checkpoint_id` (VARCHAR 255): Parent checkpoint reference
- `type` (VARCHAR 255): Checkpoint type
- `checkpoint` (LONGBLOB): Serialized checkpoint data
- `meta` (LONGBLOB): Checkpoint metadata (renamed from metadata to avoid SQLAlchemy reserved name)

### 4. checkpoint_writes
Pending checkpoint writes for LangGraph.
- `thread_id` (VARCHAR 255): Thread identifier
- `checkpoint_ns` (VARCHAR 255): Checkpoint namespace
- `checkpoint_id` (VARCHAR 255): Checkpoint identifier
- `task_id` (VARCHAR 255): Task identifier
- `idx` (INT): Write index
- `channel` (VARCHAR 255): Channel name
- `type` (VARCHAR 255): Write type
- `value` (LONGBLOB): Serialized write value

## Setup Instructions

### Prerequisites
- MySQL Server 5.7+ or MySQL 8.0+ installed and running
- Python 3.8+ with SQLAlchemy support

### Step 1: Configure Environment Variables

Copy `.env.example` to `.env` and update the MySQL configuration:

```bash
cp .env.example .env
```

Edit `.env` and set your MySQL credentials:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=chatbot_db
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

Run the database initialization script (uses SQLAlchemy ORM):

```bash
python -m database.init_db
```

This will:
1. Create the `chatbot_db` database if it doesn't exist
2. Use SQLAlchemy ORM models to create all required tables automatically
3. Set up indexes and foreign keys from model definitions
4. Verify that all tables were created successfully

**Note**: The schema is now defined in [database/models.py](models.py) using SQLAlchemy ORM models, not SQL files.

### Step 4: Start the Application

After successful database initialization, start the application:

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

## Manual Database Setup (Alternative)

If you prefer to set up the database manually:

1. Log into MySQL:
```bash
mysql -u root -p
```

2. Create the database:
```sql
CREATE DATABASE chatbot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Run the initialization script to create tables:
```bash
python -m database.init_db
```

SQLAlchemy will automatically create all tables from the ORM models defined in [database/models.py](models.py).

## Troubleshooting

### Connection Issues

If you encounter connection errors:

1. Verify MySQL is running:
```bash
# Windows
net start MySQL

# Linux
sudo systemctl status mysql
```

2. Check credentials in `.env` file
3. Ensure the MySQL user has proper privileges:
```sql
GRANT ALL PRIVILEGES ON chatbot_db.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

### Schema Issues

If tables are missing or corrupted:

1. Drop the database and recreate:
```sql
DROP DATABASE IF EXISTS chatbot_db;
CREATE DATABASE chatbot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Run the initialization script again:
```bash
python -m database.init_db
```

SQLAlchemy will recreate all tables from the ORM models.

## Migration from SQLite

If you're migrating from the previous SQLite version:

1. The old `chatbot.db` SQLite file is no longer used
2. Thread data will need to be recreated as the schema is different
3. You can safely delete `chatbot.db` after verifying MySQL works

## Maintenance

### Backup Database

```bash
mysqldump -u root -p chatbot_db > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
mysql -u root -p chatbot_db < backup_file.sql
```

### Clear All Data (Keep Schema)

```sql
USE chatbot_db;
TRUNCATE TABLE checkpoint_writes;
TRUNCATE TABLE checkpoints;
TRUNCATE TABLE document_metadata;
TRUNCATE TABLE thread_metadata;
```
