import json

try:
    with open("config.json") as file:
        settings = json.load(file.read())
except:
    print("Configuration file not found")
    settings = {}
    print("What is your future db file name?")
    settings['db_file'] = input()
    print("What is your bot token?")
    settings['token'] = input()
    print("What is your bot name?")
    settings['bot_name'] = input()
    print("What is your discord id(you can only get it in dev mode)?")
    settings['id'] = input()
    print("Which prefix do you want to use?")
    settings['prefix'] = input()
    print("What is your Google News api key?")
    settings['NEWS_API_KEY'] = input()
    with open("config.json", "w+") as file:
        file.write(json.dump(settings))
    