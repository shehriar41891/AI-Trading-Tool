from .connection import database_connection

# Connect to MongoDB
db = database_connection()
if db is None:
    print("Database connection failed. Exiting...")
    exit()

collection = db["stocks"]

def add_to_db(stock_name, stock_id):
    """Inserts or updates a stock record in MongoDB."""
    try:
        collection.update_one(
            {"_id": stock_id}, 
            {"$set": {"name": stock_name}}, 
            upsert=True
        )
        print(f"Stock {stock_id} - {stock_name} added/updated successfully!")
    except Exception as e:
        print(f"Error inserting {stock_id}: {e}")

def delete_from_db(stock_id):
    """Deletes a stock record from MongoDB using its ID."""
    try:
        result = collection.delete_one({"_id": stock_id})
        if result.deleted_count > 0:
            print(f"Stock {stock_id} deleted successfully!")
        else:
            print(f"⚠ Stock {stock_id} not found.")
    except Exception as e:
        print(f"Error deleting {stock_id}: {e}")

def find_all_stocks():
    """Retrieve all the stocks from the database."""
    try:
        stocks = list(collection.find({}, {"_id": 1, "name": 1}))  # Fetch only relevant fields
        if stocks:
            print(f"Successfully retrieved {len(stocks)} stocks.")
            return stocks
        else:
            print("No stocks found in the collection.")
            return []
    except Exception as e:
        print(f"Error retrieving stocks: {e}")
        return []

