import json

try:
    with open("config.json") as file:
        settings = json.load(file)
except FileNotFoundError:
    print("Configuration file not found")
    settings = {}

    print("What is your future db file name?")
    settings['db_file'] = input()

    print("What is your bot token?")
    settings['token'] = input()

    print("What is your bot name?")
    settings['bot_name'] = input()

    print("What is your discord id(you can only get it in dev mode)?")
    settings['id'] = int(input())

    print("Which prefix do you want to use?")
    settings['prefix'] = input()

    print("What is your Google News api key?")
    settings['NEWS_API_KEY'] = input()

    print("How much messages user must send to get new level?")
    settings['messages_per_level'] = int(input())

    print("How much money user will get for new level?")
    settings['level_reward'] = int(input())

    with open("config.json", "w+") as file:
        json.dump(settings, file)
