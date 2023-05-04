# LeetCode Discord Bot
The LeetCode Discord Bot is a Discord bot designed to help users practice coding problems from LeetCode by providing daily challenges and tracking their progress. The bot selects a random set of LeetCode problems every day and allows users to report their performance on these problems. The bot also offers a leaderboard and progress charts to visualize users' performance and improvement over time.

# Features
- Daily LeetCode problems with a range of difficulties
- Performance tracking and progress visualization
- Leaderboard to encourage friendly competition
- Customizable command prefix and problem difficulties

# Usage
To use the LeetCode Discord Bot, follow the steps below:

1. Invite the bot to your Discord server.
2. Use the following commands to interact with the bot:
- !leet: Generates a set of daily LeetCode problems and sends them to the channel.
- !solved <problem_id> <percentile>: Reports your performance on a problem by providing the problem ID and your percentile (e.g., !solved 26 99.9).
- !leaderboard: Displays a leaderboard of all active participants based on the number of problems solved.
- !progress: Plots your progress over time, displaying the number of problems solved by difficulty level.

# Installation
To set up your own instance of the LeetCode Discord Bot, follow these steps:

1. Clone the repository and install the required dependencies:
```bash
git clone https://github.com/yourusername/leetcode-discord-bot.git
cd leetcode-discord-bot
pip install -r requirements.txt
```
2. Create a Discord bot and obtain its token. Follow the instructions in the Discord Developer Portal.
3. Configure the config.json file with your bot token, command prefix, LeetCode session, and CSRF token. Optionally, you can also customize the problem difficulties.

```json
Copy code
{
  "TOKEN": "your_bot_token_here",
  "prefix": "!",
  "leetcode_session": "your_leetcode_session_here",
  "csrf_token": "your_csrf_token_here",
  "problem_difficulties": {
    "easy": true,
    "medium": true,
    "hard": true
  }
}
```
4. Invite the bot to your Discord server by following the instructions in the Discord Developer Portal.
5. Run the bot:
```bash
python main.py
```

Now your bot should be running, and you can use it on your server!