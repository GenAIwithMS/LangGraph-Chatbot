# Migration Guide: SQLite to MySQL

This document explains the changes made to migrate from SQLite to MySQL and how to set up the new database.

## What Changed

### 1. Database System
- **Before**: SQLite (`chatbot.db`)
- **After**: MySQL database (`chatbot_db`)

### 2. Files Removed/Deprecated
- `chatbot.db` - Old SQLite database (can be safely deleted after migration)
- `chatbot.db-shm` - SQLite shared memory file
- `chatbot.db-wal` - SQLite write-ahead log

### 3. New Files Added
- `database/` directory containing:
  - `models.py` - SQLAlchemy ORM models (defines database schema)
  - `init_db.py` - Database initialization script
  - `config.py` - Database configuration with connection pooling
  - `mysql_checkpoint.py` - Custom MySQL checkpoint saver using SQLAlchemy
  - `README.md` - Detailed database documentation
  - `__init__.py` - Package initialization

### 4. Modified Files
- `app/services/chatbot_service.py` - Updated to use SQLAlchemy ORM instead of raw MySQL
- `requirements.txt` - Added `sqlalchemy` and `pymysql`, removed `mysql-connector-python`
- `.env.example` - Added MySQL configuration variables
- `README.md` - Updated with MySQL and SQLAlchemy setup instructions

## New Database Schema

### Tables Created

1. **thread_metadata**
   - Stores conversation thread titles and timestamps
   - Primary key: `thread_id`
   - Includes `created_at` and `updated_at` timestamps

2. **document_metadata**
   - Stores uploaded document information per thread
   - Foreign key to `thread_metadata`
   - Tracks filename, document count, chunks count

3. **checkpoints**
   - LangGraph checkpoint storage
   - Stores conversation state for recovery
   - Composite primary key: `(thread_id, checkpoint_ns, checkpoint_id)`

4. **checkpoint_writes**
   - Pending checkpoint writes for LangGraph
   - Foreign key to `checkpoints`
   - Stores incremental state updates

## Migration Steps

### 1. Install MySQL
If you don't have MySQL installed:
- Download from: https://dev.mysql.com/downloads/mysql/
- Or use Docker: `docker run --name mysql -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.0`

### 2. Update Environment Variables
Edit your `.env` file and add:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=chatbot_db
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install `sqlalchemy` and `pymysql`.

### 4. Initialize Database
```bash
python -m database.init_db
```

This will:
- Create the `chatbot_db` database
- Create all required tables
- Set up indexes and foreign keys
- Verify the setup

### 5. Test the Application
```bash
python main.py
```

Check that the backend starts without errors.

## Data Migration (Optional)

The new MySQL database starts fresh. If you need to preserve old conversations from SQLite:

### Option 1: Manual Export (Recommended for Important Threads)
1. Open the old SQLite database:
   ```bash
   sqlite3 chatbot.db
   ```

2. Export thread metadata:
   ```sql
   .mode csv
   .output threads.csv
   SELECT * FROM thread_metadata;
   .quit
   ```

3. Import to MySQL:
   ```bash
   mysql -u root -p chatbot_db
   ```
   ```sql
   LOAD DATA INFILE 'threads.csv'
   INTO TABLE thread_metadata
   FIELDS TERMINATED BY ','
   ENCLOSED BY '"'
   LINES TERMINATED BY '\n'
   IGNORE 1 ROWS;
   ```

### Option 2: Start Fresh (Recommended)
Simply start using the new MySQL database. Old conversations in SQLite will not be accessible but files remain for reference.

## Cleanup

After verifying MySQL is working properly, you can safely delete old SQLite files:

```bash
# Windows
del chatbot.db chatbot.db-shm chatbot.db-wal

# Linux/Mac
rm chatbot.db chatbot.db-shm chatbot.db-wal
```

## Troubleshooting

### Connection Refused
- Verify MySQL is running: `mysql -u root -p`
- Check host and port in `.env`
- Ensure MySQL is accepting connections

### Authentication Failed
- Verify username and password in `.env`
- Grant privileges: `GRANT ALL PRIVILEGES ON chatbot_db.* TO 'user'@'localhost';`

### Import Errors
- Ensure `sqlalchemy` and `pymysql` are installed: `pip install sqlalchemy pymysql`
- Check Python version (3.8+)

### Missing Tables
- Re-run initialization: `python -m database.init_db`
- Check for error messages during initialization

## Benefits of MySQL

1. **Better Performance**: Handles concurrent connections better than SQLite
2. **Scalability**: Can be hosted on separate server
3. **Production Ready**: Suitable for deployment
4. **Advanced Features**: Better indexing, full-text search capabilities
5. **Reliability**: ACID compliance with InnoDB engine
6. **Backup**: Standard MySQL backup tools available

## Benefits of SQLAlchemy

1. **ORM**: Work with Python objects instead of raw SQL
2. **Connection Pooling**: Automatic connection reuse and management
3. **Database Abstraction**: Easy to switch between databases
4. **Type Safety**: Better IDE support and type hints
5. **Maintainability**: Centralized schema in Python models
6. **Security**: Automatic SQL injection prevention

## Rollback (If Needed)

If you need to rollback to SQLite temporarily:

1. Checkout the previous version from git:
   ```bash
   git log --oneline  # Find commit before MySQL migration
   git checkout <commit-hash> -- app/services/chatbot_service.py requirements.txt
   ```

2. Install old requirements:
   ```bash
   pip install langgraph-checkpoint-sqlite
   pip uninstall sqlalchemy pymysql
   ```

3. Restart the application

## Support

For detailed database setup and troubleshooting, see [database/README.md](database/README.md).
