import json
import discord
import datetime
from discord.ext import commands

import problems
import data

def load_config(file_path='config.json'):
	with open(file_path, 'r') as config_file:
		return json.load(config_file)

def run_discord_bot():
	config = load_config()
	leetcode_api = problems.init_leetcode_api(config['leetcode_session'], config['csrf_token'])
	intents = discord.Intents.default()
	intents.messages = True
	bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

	# Initialize the database
	db_conn = data.init_db()
	print("Database initialized.")

	@bot.event
	async def on_ready():
		print(f'{bot.user.name} has connected to Discord!')

	@bot.command(name='leet')
	async def leet(ctx):
		"""Provides the daily leetcode problems."""
		# Get a random unsolved question for each difficulty level
		difficulty_levels = [key.title() for key, value in config["problem_difficulties"].items() if value]
		leet_problems = problems.get_random_unsolved_questions(leetcode_api, difficulty_levels)

		# Add the problems to the daily problems table
		daily_problems_ids = [problem_info['id'] for problem_info in leet_problems.values()]
		data.add_daily_problems(db_conn, daily_problems_ids)

		# Create an embed object
		embed = discord.Embed(
			title="Today's LeetCode Problems",
			description=f"Here are today's problems, {ctx.author.mention}:",
			color=discord.Color.blue()
		)

		# Add fields to the embed for each problem
		for difficulty, problem_info in leet_problems.items():
			problem_id = problem_info['id']
			problem_level = problem_info['level']
			problem_title = problem_info['title']
			problem_url = problem_info['url']
			acceptance_rate = problem_info['acceptance_rate']
			data.add_leetcode_problem(db_conn, problem_id, problem_title, problem_level)

			# Add a field to the embed for the current problem
			field_name = f"{difficulty} [#{problem_id}] ({acceptance_rate}% acceptance rate)"
			field_value = f"[{problem_title}]({problem_url})"
			embed.add_field(name=field_name, value=field_value, inline=False)

		# Send the embed message
		await ctx.send(embed=embed)

	@bot.command(name='solved')
	async def report_score(ctx):
		"""Reports the user's performance on a problem."""
		message = ctx.message
		try:
			# Parse the message and make sure it's valid
			_, problem_id, percentile = message.content.split()
			percentile = float(percentile)
			if percentile < 0 or percentile > 100:
				raise Exception("Percentile should be between 0 and 100.")
			percentile = round(percentile, 1)

			# Make sure that the problem is one of today's problems
			daily_problems = data.get_daily_problems(db_conn)
			if int(problem_id) not in daily_problems:
				raise Exception(f"Problem {problem_id} is not one of today's problems.")

			# Get the problem level and timestamp
			level = data.get_problem_level_by_id(db_conn, problem_id)
			timestamp = datetime.datetime.now().date()

			# Add data to the database, and send a confirmation message
			data.add_user(db_conn, message.author.id, message.author.name)
			data.add_user_problem(db_conn, message.author.id, int(problem_id), float(percentile), timestamp, level)
			await message.channel.send(f"{message.author.mention} Successfully added problem {problem_id} with {percentile}% performance.")
		except Exception as e:
			print(f"Exception: {e}")
			await message.channel.send(f"{message.author.mention} Error: {str(e)}\n\n"
										"Usage: !solved <problem_id> <percentile>\n"
										"Ensure your problem_id is from today, and that your percentile is between 0 and 100.\n")

	@bot.command(name='leaderboard')
	async def leaderboard(ctx):
		"""Provides a leaderboard of all active participants."""
		# Create the bar chart and save it to disk
		data.plot_leaderboard(db_conn)

		# Send the image file as a message in the Discord channel
		with open('bar_chart.png', 'rb') as img_file:
			await ctx.send(file=discord.File(img_file, 'bar_chart.png'))

	@bot.command(name='progress')
	async def progress(ctx):
		"""Plots the user's progress over time."""
		user_id = ctx.author.id
		data.plot_user_progress(db_conn, user_id)

		with open('progress.png', 'rb') as img_file:
			await ctx.send(file=discord.File(img_file, 'progress.png'))

	bot.run(config['TOKEN'])


if __name__ == "__main__":
	run_discord_bot()