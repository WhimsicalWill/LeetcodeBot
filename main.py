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
        
        print(f"Fetching random unsolved problems for difficulty levels: {difficulty_levels}")
        leet_problems = problems.get_random_unsolved_questions(leetcode_api, difficulty_levels)
        print(f"Found {len(leet_problems)} random unsolved problems.")
        print(leet_problems)

        # Format the problem information as a message
        message = f"{ctx.author.mention} Here are today's problems:\n\n"
        for difficulty, problem_info in leet_problems.items():
            problem_id = problem_info['id']
            problem_level = problem_info['level']
            problem_title = problem_info['title']
            acceptance_rate = problem_info['acceptance_rate']
            data.add_leetcode_problem(db_conn, problem_id, problem_title, problem_level)
            print(f"Added problem {problem_id}, of difficulty {difficulty} to database.")
            message += f"**{difficulty} [#{problem_id}]:** **{problem_title}**, ({acceptance_rate}%)\n" \
                       f"(<https://leetcode.com/problems/{problem_title.lower().replace(' ', '-')}/{problem_id}>)\n"

        await ctx.send(message)

    @bot.command(name='solved')
    async def report_score(ctx):
        """Reports the user's performance on a problem."""
        message = ctx.message
        try:
            _, problem_id, percentile = message.content.split()
            # TODO: refactor this to level (since level is numeric, difficulty is string)
            difficulty = data.get_problem_difficulty_by_id(db_conn, problem_id)
            timestamp = datetime.datetime.now().date()
            data.add_user_problem(db_conn, message.author.id, int(problem_id), float(percentile), timestamp, difficulty)
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