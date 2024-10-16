import asyncpg
# import asyncio
import json

# Load configuration file
with open("config.json") as json_file:
    config = json.load(json_file)

# Database configuration
HOST = config["HOST"]
DB = config["database"]
USER = config["user"]
PASSWORD = config["password"]


# Function to establish connection to the PostgreSQL database
async def get_connection():
    return await asyncpg.connect(
        host=HOST,
        database=DB,
        user=USER,
        password=PASSWORD
    )


# Function to initialize the database schema
async def initialize_database():
    conn = await get_connection()
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
    finally:
        await conn.close()


# Function to store messages in the database
async def store_message(user_id: str, role: str, message: str):
    conn = await get_connection()
    try:
        await conn.execute('''
            INSERT INTO conversation_history (user_id, role, message)
            VALUES ($1, $2, $3)
        ''', user_id, role, message)
    finally:
        await conn.close()


# Function to retrieve conversation history from the database
async def get_conversation_history(user_id: str):
    conn = await get_connection()
    try:
        rows = await conn.fetch('''
            SELECT role, message
            FROM conversation_history
            WHERE user_id = $1
            ORDER BY timestamp
        ''', user_id)
        return [(row['role'], row['message']) for row in rows]
    finally:
        await conn.close()

# Example of initializing the database
# asyncio.run(initialize_database())
