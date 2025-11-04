import sqlite3
from werkzeug.security import generate_password_hash

def init_database():
    conn = sqlite3.connect('examproctordb.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Role TEXT DEFAULT 'STUDENT'
        )
    ''')
    
    # Insert sample admin user (hashed password)
    cursor.execute(
        'INSERT OR IGNORE INTO students (Name, Email, Password, Role) VALUES (?, ?, ?, ?)',
        ('Admin', 'admin@example.com', generate_password_hash('admin123'), 'ADMIN')
    )
    
    # Insert sample student user (hashed password)
    cursor.execute(
        'INSERT OR IGNORE INTO students (Name, Email, Password, Role) VALUES (?, ?, ?, ?)',
        ('John Doe', 'student@example.com', generate_password_hash('student123'), 'STUDENT')
    )
    
    conn.commit()

    # One-time migration: hash any plaintext passwords detected
    try:
        cursor.execute('SELECT ID, Password FROM students')
        rows = cursor.fetchall()
        for sid, pwd in rows:
            # Werkzeug hashes start with 'pbkdf2:' typically; if not, hash it
            if pwd is not None and not str(pwd).startswith('pbkdf2:'):
                cursor.execute('UPDATE students SET Password=? WHERE ID=?', (generate_password_hash(pwd), sid))
        conn.commit()
    except Exception:
        pass
    conn.close()
    print("Database initialized successfully!")
    print("Admin login: admin@example.com / admin123")
    print("Student login: student@example.com / student123")

if __name__ == '__main__':
    init_database()
