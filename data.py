import matplotlib.pyplot as plt
import sqlite3
import datetime
import numpy as np
from collections import defaultdict

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
        timestamp DATE NOT NULL,
        difficulty INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leetcode_problems (
        problem_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        difficulty TEXT NOT NULL
    );
    """)

    conn.commit()

    return conn

def add_user(db_conn, user_id, username):
    with db_conn:
        db_conn.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

def add_user_problem(db_conn, user_id, problem_id, percentile, timestamp, difficulty):
    print(f"Adding user problem: {user_id}, {problem_id}, {percentile}, {timestamp}, {difficulty}")
    with db_conn:
        db_conn.execute("INSERT INTO user_problems (user_id, problem_id, percentile, timestamp, difficulty) VALUES (?, ?, ?, ?, ?)", (user_id, problem_id, percentile, timestamp, difficulty))

def get_problem_difficulty_by_id(db_conn, problem_id):
    with db_conn:
        result = db_conn.execute("SELECT difficulty FROM leetcode_problems WHERE problem_id = ?", (problem_id,)).fetchone()
    if result is None:
        raise Exception(f"Problem {problem_id} not found in database")
    return result[0]

def add_leetcode_problem(db_conn, problem_id, title, difficulty):
    with db_conn:
        db_conn.execute("INSERT OR IGNORE INTO leetcode_problems (problem_id, title, difficulty) VALUES (?, ?, ?)", (problem_id, title, difficulty))

def get_user_problem_counts(db_conn):
    with db_conn:
        return db_conn.execute("""
        SELECT username, COUNT(*) as problem_count
        FROM user_problems
        JOIN users ON users.user_id = user_problems.user_id
        GROUP BY users.user_id
        ORDER BY problem_count DESC
        """).fetchall()

def get_user_progress(db_conn, user_id):
    with db_conn:
        return db_conn.execute("""
        SELECT date(timestamp, 'start of day') as date, difficulty, COUNT(DISTINCT problem_id) as problem_count
        FROM user_problems
        WHERE user_id = ?
        GROUP BY date, difficulty
        ORDER BY date
        """, (user_id,)).fetchall()

def plot_leaderboard(db_conn):
    user_problem_counts = get_user_problem_counts(db_conn)
    print(user_problem_counts)
    usernames = [user[0] for user in user_problem_counts]
    problem_counts = [user[1] for user in user_problem_counts]

    plt.bar(usernames, problem_counts)
    plt.xlabel('Users')
    plt.ylabel('Problems Solved')
    plt.title('Number of Problems Solved by Each User')
    plt.savefig('bar_chart.png')
    plt.close()

def plot_user_progress(db_conn, user_id):
    user_progress = get_user_progress(db_conn, user_id)
    problems_per_day = defaultdict(lambda: [0, 0, 0]) # date -> [easy, medium, hard]

    for date_str, difficulty, count in user_progress:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        if difficulty == 1: # Easy
            problems_per_day[date][0] = count
        elif difficulty == 2: # Medium
            problems_per_day[date][1] = count
        elif difficulty == 3: # Hard
            problems_per_day[date][2] = count

    dates = problems_per_day.keys()
    easy_count = [problems_per_day[date][0] for date in dates]
    medium_count = [problems_per_day[date][1] for date in dates]
    hard_count = [problems_per_day[date][2] for date in dates]

    # Set x-axis tick labels and rotation angle
    plt.xticks(rotation=90)

    plt.plot(dates, easy_count, label='Easy')
    plt.plot(dates, medium_count, label='Medium')
    plt.plot(dates, hard_count, label='Hard')

    plt.xlabel('Date')
    plt.ylabel('Problems Solved')
    plt.title('User Progress')
    plt.legend()

    plt.savefig('progress.png')
    plt.close()