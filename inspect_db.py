import database
import sqlite3

p = str(database.DB_PATH)
print('DB path:', p)
conn = sqlite3.connect(p)
c = conn.cursor()
try:
    c.execute('SELECT count(*) FROM predictions')
    print('predictions_count:', c.fetchone()[0])
    c.execute('SELECT id, user_id, is_guest, predicted_category, confidence, created_at FROM predictions')
    rows = c.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print('error querying predictions:', e)
conn.close()
