import matplotlib.pyplot as plt
import sqlite3
import datetime
import numpy as np

def get_user_progress(db_conn, user_id):
    with db_conn:
        return db_conn.execute("""
        SELECT date(timestamp, 'start of day') as date, problem_id, percentile
        FROM user_problems
        WHERE user_id = ?
        GROUP BY date, problem_id
        ORDER BY date
        """, (user_id,)).fetchall()

def plot_user_progress(db_conn, user_id):
    user_progress = get_user_progress(db_conn, user_id)
    dates = []
    easy_count, medium_count, hard_count = [], [], []

    easy, medium, hard = 0, 0, 0

    for i, entry in enumerate(user_progress):
        date, problem_id, percentile = entry
        date = datetime.datetime.strptime(date, '%Y-%m-%d')

        problem = api_instance.api_problems_problem_id_get(problem_id) # Get problem details
        if problem.difficulty.level == 1: # Easy
            easy += 1
        elif problem.difficulty.level == 2: # Medium
            medium += 1
        elif problem.difficulty.level == 3: # Hard
            hard += 1

        dates.append(date)
        easy_count.append(easy)
        medium_count.append(medium)
        hard_count.append(hard)

    plt.plot(dates, easy_count, label='Easy')
    plt.plot(dates, medium_count, label='Medium')
    plt.plot(dates, hard_count, label='Hard')

    plt.xlabel('Date')
    plt.ylabel('Problems Solved')
    plt.title('User Progress')
    plt.legend()

    plt.savefig('progress.png')
    plt.close()

def init_db(db_name="user_problems.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_problems (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        percentile REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    conn.commit()

    return conn

def add_user(db_conn, user_id, username):
    with db_conn:
        db_conn.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

def add_user_problem(db_conn, user_id, problem_id, percentile):
    with db_conn:
        db_conn.execute("INSERT INTO user_problems (user_id, problem_id, percentile) VALUES (?, ?, ?)", (user_id, problem_id, percentile))

def get_user_problems(db_conn, user_id):
    with db_conn:
        return db_conn.execute("SELECT problem_id, percentile FROM user_problems WHERE user_id = ?", (user_id,)).fetchall()

def get_user_problem_counts(db_conn):
    with db_conn:
        return db_conn.execute("""
        SELECT username, COUNT(*) as problem_count
        FROM user_problems
        JOIN users ON users.user_id = user_problems.user_id
        GROUP BY users.user_id
        ORDER BY problem_count DESC
        """).fetchall()

def plot_leaderboard():
    user_problem_counts = get_user_problem_counts()
    usernames = [user[0] for user in user_problem_counts]
    problem_counts = [user[1] for user in user_problem_counts]

    plt.bar(usernames, problem_counts)
    plt.xlabel('Users')
    plt.ylabel('Problems Solved')
    plt.title('Number of Problems Solved by Each User')
    plt.savefig('bar_chart.png')
    plt.close()
