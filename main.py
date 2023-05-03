import random
import json
import discord
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

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')

    @bot.command(name='leet')
    async def leet(ctx):
        # Get the random unsolved question and send it
        _, problem_url = problems.get_random_unsolved_question(leetcode_api)
        await ctx.send(problem_url)

    @bot.command(name='solved')
    async def report_score(ctx):
        message = ctx.message
        try:
            _, problem_id, percentile_performance = message.content.split()
            data.add_user_problem(message.author.id, int(problem_id), float(percentile_performance))
        except ValueError:
            await message.channel.send(f"{message.author.mention} Invalid message format.\n\
                                        Please use: !solved <problem_id> <percentile> (ex: !solved 1 99.9)")

    @bot.command(name='leaderboard')
    async def leaderboard(ctx):
        # Create the bar chart and save it to disk
        data.plot_leaderboard()

        # Send the image file as a message in the Discord channel
        with open('bar_chart.png', 'rb') as img_file:
            await ctx.send(file=discord.File(img_file, 'bar_chart.png'))

    @bot.command(name='progress')
    async def progress(ctx):
        user_id = ctx.author.id
        data.plot_user_progress(db_conn, user_id)

        with open('progress.png', 'rb') as img_file:
            await ctx.send(file=discord.File(img_file, 'progress.png'))

    @bot.command(name='help')
    async def help(ctx):
        await ctx.send(f"{ctx.author.mention} Commands:\n\
                        !leet - get a random unsolved LeetCode problem\n\
                        !solved <problem_id> <percentile> - report your performance on a problem\n\
                        !leaderboard - see the leaderboard\n\
                        !progress - see your progress")

    bot.run(config['TOKEN'])


if __name__ == "__main__":
    run_discord_bot()