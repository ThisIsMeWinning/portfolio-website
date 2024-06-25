from sqlalchemy import text
from app import db, app

def drop_new_user_table():
    with app.app_context():
        connection = db.engine.connect()
        connection.execute(text("DROP TABLE IF EXISTS new_user"))

if __name__ == '__main__':
    drop_new_user_table()
