from app import db, app
from sqlalchemy import text

def drop_is_admin_column():
    with app.app_context():
        connection = db.engine.connect()
        try:
            result = connection.execute(text("ALTER TABLE user DROP COLUMN is_admin"))
            print("Dropped is_admin column from user table.")
        except Exception as e:
            print(f"Error: {e}")
        connection.close()

if __name__ == "__main__":
    drop_is_admin_column()
