import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sqlite3
import datetime
import numpy as np

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
		level INTEGER NOT NULL,
		FOREIGN KEY (user_id) REFERENCES users (user_id)
	);
	""")

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS leetcode_problems (
		problem_id INTEGER PRIMARY KEY,
		title TEXT NOT NULL,
		level TEXT NOT NULL
	);
	""")

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS daily_problems (
		problem_id INTEGER PRIMARY KEY,
		level INTEGER NOT NULL,
		FOREIGN KEY (problem_id) REFERENCES leetcode_problems (problem_id)
	);
	""")

	conn.commit()
	return conn

def add_user(db_conn, user_id, username):
	with db_conn:
		db_conn.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

def add_user_problem(db_conn, user_id, problem_id, percentile, timestamp, level):
	print(f"Adding user problem: {user_id}, {problem_id}, {percentile}, {timestamp}, {level}")
	with db_conn:
		existing_record = db_conn.execute("SELECT id FROM user_problems WHERE user_id = ? AND problem_id = ?", (user_id, problem_id)).fetchone()
		if existing_record:
			db_conn.execute("UPDATE user_problems SET percentile = ? WHERE id = ?", (percentile, existing_record[0]))
		else:
			db_conn.execute("INSERT INTO user_problems (user_id, problem_id, percentile, timestamp, level) VALUES (?, ?, ?, ?, ?)", (user_id, problem_id, percentile, timestamp, level))

def add_leetcode_problem(db_conn, problem_id, title, level):
	with db_conn:
		db_conn.execute("INSERT OR IGNORE INTO leetcode_problems (problem_id, title, level) VALUES (?, ?, ?)", (problem_id, title, level))

def add_daily_problems(db_conn, problems):
	with db_conn:
		db_conn.execute("DELETE FROM daily_problems")
		for problem_id, level in problems:
			db_conn.execute("INSERT INTO daily_problems (problem_id, level) VALUES (?, ?)", (problem_id, level))

	db_conn.commit()

def get_problem_level_by_id(db_conn, problem_id):
	with db_conn:
		result = db_conn.execute("SELECT level FROM leetcode_problems WHERE problem_id = ?", (problem_id,)).fetchone()
	if result is None:
		raise Exception(f"Problem {problem_id} not found in database")
	return result[0]

def get_daily_problems(db_conn):
	with db_conn:
		return {row[0]: row[1] for row in db_conn.execute("SELECT level, problem_id FROM daily_problems").fetchall()}

def get_daily_problems_with_difficulty(db_conn):
	with db_conn:
		return {row[0].lower(): row[1] for row in db_conn.execute("""
			SELECT level, problem_id
			FROM daily_problems
			JOIN leetcode_problems ON daily_problems.problem_id = leetcode_problems.problem_id
		""").fetchall()}

def get_user_problem_counts(db_conn):
	with db_conn:
		return db_conn.execute("""
		SELECT username, COUNT(*) as problem_count
		FROM user_problems
		JOIN users ON users.user_id = user_problems.user_id
		GROUP BY username
		ORDER BY problem_count DESC
		""").fetchall()

def get_user_progress(db_conn, user_id):
	with db_conn:
		return db_conn.execute("""
		SELECT date(timestamp, 'start of day') as date, level, COUNT(DISTINCT problem_id) as problem_count
		FROM user_problems
		WHERE user_id = ?
		GROUP BY date, level
		ORDER BY date
		""", (user_id,)).fetchall()

def get_tick_interval(x):
	return max(1, int(5 * round(x / 25)))

def plot_leaderboard(db_conn):
	user_problem_counts = get_user_problem_counts(db_conn)
	usernames = [user[0] for user in user_problem_counts]
	problem_counts = [user[1] for user in user_problem_counts]

	# Generate a list of colors using a colormap
	cmap = mcolors.ListedColormap(['darkgreen', 'lightgreen', 'yellow', 'orange', 'red', 'gray'])
	colors = [cmap(i % cmap.N) for i in range(len(usernames))]

	plt.figure(figsize=(8, 6))  # adjust the figure size as needed
	plt.barh(usernames, problem_counts, color=colors)
	plt.xlabel('Problems Solved')
	plt.ylabel('Users')
	plt.title('Leetcode Leaderboard')
	
	# Set axis ticks
	xticks = np.arange(0, max(problem_counts) + 1, step=get_tick_interval(max(problem_counts)))
	plt.gca().set_xticks(xticks)
	plt.gca().invert_yaxis()  # reverse the order of the bars
	plt.gca().tick_params(axis='y', labelsize=8)  # adjust the font size of the y-axis labels as needed

	plt.tight_layout()
	plt.savefig('bar_chart.png')
	plt.close()

def plot_user_progress(db_conn, user_id):
	user_progress = get_user_progress(db_conn, user_id)
	counts = [0, 0, 0]
	cum_problems = {} # date -> [easy, medium, hard] counts

	for date_str, level, count in user_progress:
		date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
		counts[level - 1] += count
		cum_problems[date] = counts.copy()

	dates = cum_problems.keys()
	easy_count = [cum_problems[date][0] for date in dates]
	medium_count = [cum_problems[date][1] for date in dates]
	hard_count = [cum_problems[date][2] for date in dates]

	# Set axis ticks
	plt.xticks([])
	yticks = np.arange(0, max(counts) + 1, step=get_tick_interval(max(counts)))
	plt.gca().set_yticks(yticks)

	plt.plot(dates, easy_count, label='Easy')
	plt.plot(dates, medium_count, label='Medium')
	plt.plot(dates, hard_count, label='Hard')

	plt.xlabel('Date')
	plt.ylabel('Problems Solved')
	plt.title('User Progress')
	plt.legend()

	plt.savefig('progress.png')
	plt.close()
