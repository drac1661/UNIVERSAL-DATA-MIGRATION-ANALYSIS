// MongoDB initialization script
// This script runs automatically when MongoDB container starts

// Get environment variables (defaults provided for local development)
const rootUsername = 'drac1661';
const rootPassword = 'Drac1661@';
const dbName = 'udm_dev';

// Initialize the database
db = db.getSiblingDB(dbName);

// Create application user for the database (optional)
// This creates a user that can read/write only to this database
db.createUser({
  user: 'udm_dev',
  pwd: 'Drac1661@',
  roles: [
    {
      role: 'readWrite',
      db: dbName
    }
  ]
});

// Create initial collections if needed (optional)
// Uncomment to create collections on startup
/*
db.createCollection('users');
db.createCollection('orders');
db.createCollection('products');
*/

// Create indexes (optional)
// Uncomment to create indexes on startup
/*
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ user_id: 1 });
db.orders.createIndex({ created_at: -1 });
*/

print(`✓ Database '${dbName}' initialized successfully`);
print(`✓ User 'udm_user' created with read/write access`);
