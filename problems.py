import random
import json
import leetcode

def init_leetcode_api(leetcode_session, csrf_token):
    configuration = leetcode.Configuration()
    configuration.api_key["x-csrftoken"] = csrf_token
    configuration.api_key["csrftoken"] = csrf_token
    configuration.api_key["LEETCODE_SESSION"] = leetcode_session
    configuration.api_key["Referer"] = "https://leetcode.com"
    configuration.debug = False

    api = leetcode.DefaultApi(leetcode.ApiClient(configuration))
    return api

def get_random_unsolved_questions(api, difficulties):
    # Fetch the list of problems
    api_response = api.api_problems_topic_get(topic="algorithms")

    # Filter out the problems that have been solved already
    unsolved_problems = [
        pair for pair in api_response.stat_status_pairs if pair.status != "ac"
    ]

    # For converting the difficulty level to a number, which leetcode uses
    levels = {'Easy': 1, 'Medium': 2, 'Hard': 3}

    selected_problems = {}
    for difficulty in difficulties:
        level = levels[difficulty]
        for problem in unsolved_problems[:5]:
            # debug by printing out the problem difficulty
            print(f"Problem {problem.stat.frontend_question_id} has level {problem.difficulty.level}")

        # Filter the problems you haven't solved yet for the current difficulty
        diff_problems = [
            problem for problem in unsolved_problems
            if problem.status != "ac" and problem.difficulty.level == level
        ]

        if diff_problems:
            # Choose a random unsolved problem for the current difficulty
            random_problem = random.choice(unsolved_problems)

            # Get problem details
            problem_id = random_problem.stat.frontend_question_id
            problem_title = random_problem.stat.question__title
            problem_url = f"https://leetcode.com/problems/{random_problem.stat.question__title_slug}/"
            acceptance_rate = round(random_problem.stat.total_acs / random_problem.stat.total_submitted * 100, 2)

            # Add the problem information to the selected_problems dictionary
            selected_problems[difficulty] = {
                "id": problem_id,
                "level": level,
                "title": problem_title,
                "url": problem_url,
                "acceptance_rate": acceptance_rate
            }

    return selected_problems
