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
			_, problem_id, percentile = message.content.split()
			level = data.get_problem_level_by_id(db_conn, problem_id)
			timestamp = datetime.datetime.now().date()
			data.add_user(db_conn, message.author.id, message.author.name)
			data.add_user_problem(db_conn, message.author.id, int(problem_id), float(percentile), timestamp, level)
			await message.channel.send(f"{message.author.mention} Successfully added problem {problem_id} with {percentile}% performance.")
		except Exception as e:
			print(f"Exception: {e}")
			await message.channel.send(f"{message.author.mention} Invalid message. Make sure you're reporting a valid problem id.\n"
										"Also, please use: !solved <problem_id> <percentile> (ex: !solved 1 99.9)")

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