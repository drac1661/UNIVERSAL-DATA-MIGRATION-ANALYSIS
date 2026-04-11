# MongoDB Docker Setup Guide

## Quick Start

### 1. Start MongoDB with Docker Compose

```bash
cd docker
docker-compose -f docker-compose-mongo.yml up -d
```

### 2. Verify MongoDB is Running

```bash
docker logs mongodb
```

You should see output like:
```
✓ Database 'udm_dev' initialized successfully
✓ User 'udm_user' created with read/write access
```

### 3. Test Connection

```bash
# Using mongosh (MongoDB shell)
mongosh mongodb://drac1661:Drac1661@localhost:27017/udm_dev

# Or with Python
python -c "
from extractor.mongo_extractor import MongoDBExtractor
ext = MongoDBExtractor('mongo_config.json')
print('Connected successfully!')
print('Collections:', ext.get_all_collections())
ext.close()
"
```

## Configuration

### Docker Compose (docker-compose-mongo.yml)
```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: drac1661    # Root user
  MONGO_INITDB_ROOT_PASSWORD: Drac1661@   # Root password
  MONGO_INITDB_DATABASE: udm_dev          # Initial database
```

### Python Config (resources/mongo_config.json)
```json
{
  "db_type": "mongodb",
  "host": "127.0.0.1",
  "port": 27017,
  "dbname": "udm_dev",              # Matches MONGO_INITDB_DATABASE
  "user": "drac1661",               # Root user credentials
  "password": "Drac1661@",
  "auth_source": "admin"
}
```

### Initialization Script (docker/mongo-init.js)
- Creates the database (udm_dev) if it doesn't exist
- Creates application user (udm_user) with read/write access
- Ready to add custom collections and indexes

## Common Tasks

### Extract Schema from Docker MongoDB

```bash
python mongo_schema_generator_main.py \
  --config mongo_config.json \
  --schema-output schema/mongo_schema.json \
  --verbose
```

### Extract All Data

```bash
python mongo_schema_generator_main.py \
  --config mongo_config.json \
  --extract-data \
  --verbose
```

### Extract Specific Collection

```bash
python mongo_schema_generator_main.py \
  --collection users \
  --data-output data/users.json
```

### Connect with MongoDB Shell

```bash
# Root access
mongosh mongodb://drac1661:Drac1661@localhost:27017/admin

# Application user (if using init script)
mongosh mongodb://udm_user:udm_password@localhost:27017/udm_dev
```

### Add Collections on Startup

Edit `docker/mongo-init.js` and uncomment the collection creation:

```javascript
db.createCollection('users');
db.createCollection('orders');
db.createCollection('products');
```

Then restart the container.

### Add Indexes on Startup

Edit `docker/mongo-init.js` and uncomment the index creation:

```javascript
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ user_id: 1 });
db.orders.createIndex({ created_at: -1 });
```

Then restart the container.

## Usage with PostgreSQL

You can now use both PostgreSQL and MongoDB side by side:

```python
# Extract from both databases
from schema_generator import extract_schema_to_models as pg_extract
from mongo_schema_generator import extract_schema_to_models as mongo_extract

# PostgreSQL
pg_extract(config_file="db_config.json", output_file="schema/pg_schema.json")

# MongoDB
mongo_extract(config_file="mongo_config.json", output_file="schema/mongo_schema.json")
```

## Docker Management

### Stop MongoDB
```bash
docker-compose -f docker/docker-compose-mongo.yml down
```

### Remove MongoDB (including data)
```bash
docker-compose -f docker/docker-compose-mongo.yml down -v
```

### View MongoDB Logs
```bash
docker-compose -f docker/docker-compose-mongo.yml logs -f mongodb
```

### Restart MongoDB
```bash
docker-compose -f docker/docker-compose-mongo.yml restart
```

## Environment Variables

### Docker Compose Variables
| Variable | Value | Purpose |
|----------|-------|---------|
| `MONGO_INITDB_ROOT_USERNAME` | drac1661 | Root username for MongoDB |
| `MONGO_INITDB_ROOT_PASSWORD` | Drac1661@ | Root password for MongoDB |
| `MONGO_INITDB_DATABASE` | udm_dev | Initial database created |

### Python Config Variables
| Variable | Value | Purpose |
|----------|-------|---------|
| `db_type` | mongodb | Database type |
| `host` | 127.0.0.1 | MongoDB server address |
| `port` | 27017 | MongoDB port |
| `dbname` | udm_dev | Database to connect to |
| `user` | drac1661 | Username for authentication |
| `password` | Drac1661@ | Password for authentication |
| `auth_source` | admin | Authentication database |

## Modifying Configuration

### Change Database Name

1. **Docker Compose**: Update `docker-compose-mongo.yml`
   ```yaml
   environment:
     MONGO_INITDB_DATABASE: my_new_db
   ```

2. **Python Config**: Update `resources/mongo_config.json`
   ```json
   {
     "dbname": "my_new_db",
     ...
   }
   ```

3. **Init Script**: Update `docker/mongo-init.js`
   ```javascript
   const dbName = 'my_new_db';
   ```

4. **Restart Container**:
   ```bash
   docker-compose -f docker/docker-compose-mongo.yml down -v
   docker-compose -f docker/docker-compose-mongo.yml up -d
   ```

### Change Credentials

1. **Docker Compose**: Update `docker-compose-mongo.yml`
   ```yaml
   environment:
     MONGO_INITDB_ROOT_USERNAME: newuser
     MONGO_INITDB_ROOT_PASSWORD: newpass
   ```

2. **Python Config**: Update `resources/mongo_config.json`
   ```json
   {
     "user": "newuser",
     "password": "newpass",
     ...
   }
   ```

3. **Restart Container**:
   ```bash
   docker-compose -f docker/docker-compose-mongo.yml down -v
   docker-compose -f docker/docker-compose-mongo.yml up -d
   ```

## Troubleshooting

### Connection Refused
```bash
# Check if container is running
docker ps

# Check logs
docker logs mongodb

# Verify port 27017 is not blocked
netstat -an | grep 27017
```

### Authentication Failed
- Verify credentials in both `docker-compose-mongo.yml` and `mongo_config.json` match
- Ensure `auth_source` is set to "admin"
- Check MongoDB logs: `docker logs mongodb`

### Database Not Created
- Check MongoDB logs for initialization script errors
- Verify `mongo-init.js` file exists
- Check file permissions: `ls -la docker/mongo-init.js`

### Permission Denied on Init Script
```bash
chmod +r docker/mongo-init.js
docker-compose -f docker/docker-compose-mongo.yml down -v
docker-compose -f docker/docker-compose-mongo.yml up -d
```

## Files Involved

- **`docker/docker-compose-mongo.yml`** - Docker Compose configuration
- **`docker/mongo-init.js`** - Database initialization script
- **`resources/mongo_config.json`** - Python MongoDB configuration
- **`mongo_schema_generator.py`** - Schema extraction script
- **`extractor/mongo_extractor.py`** - MongoDB extractor module

## Related Documentation

- **`MONGODB_IMPLEMENTATION.md`** - Full MongoDB implementation details
- **`MONGODB_QUICK_REFERENCE.md`** - Quick reference for MongoDB features
- **PostgreSQL equivalent**: `docker/docker-compose.yml`
