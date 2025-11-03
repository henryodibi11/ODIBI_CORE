import sqlite3

conn = sqlite3.connect('D:/projects/odibi_core/resources/configs/showcases/showcase_configs.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM showcase_config')
print(f'Total rows: {cursor.fetchone()[0]}')
cursor.execute('SELECT showcase_id, step_name, layer FROM showcase_config LIMIT 5')
print('\nSample rows:')
for row in cursor.fetchall():
    print(f'  ID={row[0]}, Name={row[1]}, Layer={row[2]}')
conn.close()
