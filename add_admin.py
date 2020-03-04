import sqlite3
from config import DB_PATH


def exe_query(query):
    con_obj = sqlite3.connect(DB_PATH)
    courser = con_obj.execute(query)
    res = courser.fetchall()
    con_obj.commit()
    con_obj.close()
    return res


try:
    admin_id = int(input('Enter admin id: '))
    exe_query(f'INSERT INTO Admin (telegram_id) VALUES ({admin_id});')
    print(f'Admin ({admin_id}) added successfully!')
except ValueError:
    print('Invalid admin id')
