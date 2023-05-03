import random
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

def get_random_unsolved_question(api):
    # Fetch the list of problems
    api_response = api.api_problems_topic_get(topic="algorithms") # TODO: what other topics are there?

    # Filter the problems you haven't solved yet
    unsolved_problems = [
        pair for pair in api_response.stat_status_pairs if pair.status != "ac"
    ]

    # Choose a random unsolved problem
    random_problem = random.choice(unsolved_problems)

    # Get problem details
    problem_title = random_problem.stat.question__title
    problem_url = f"https://leetcode.com/problems/{random_problem.stat.question__title_slug}/"

    print(problem_title, problem_url)
    # TODO: what to return?
    return problem_title, problem_url
