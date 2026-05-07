import requests
import os
import json
import pyperclip

global API_KEY
API_KEY = ""

global maxTokens
global language
global headers

dataStorage = "data.txt"

#ai setup stuff
url = "https://integrate.api.nvidia.com/v1/chat/completions"
tokenSaver = "keep your response short and simple just giving me the code from this request without any explanation, usage cases, and additional comments:"

headers = {
    "Authorization": f"Bearer {API_KEY}", 
    "Content-Type": "application/json"
}

ctxString = ""

#context file paths + existing code created
file_context = []#file paths
code_generated_context = []#existing code

def load_ctx():
    global ctxString
    ctxString = ""

    for path in file_context:
        if os.path.isfile(path):
            ctxString += " " + read_file(path)

    for code in code_generated_context:
        ctxString += " " + code

    return ctxString

#load data from the data.txt file if it exists
def load_settings():
    global API_KEY
    global maxTokens
    global language
    global headers

    API_KEY = ""
    maxTokens = 200
    language = ""

    if os.path.isfile(dataStorage):
        file_context.clear()
        with open(dataStorage, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("API_KEY="):
                    API_KEY = line[len("API_KEY="):].strip()
                elif line.startswith("maxTokens="):
                    maxTokens = int(line[len("maxTokens="):].strip())
                elif line.startswith("language="):
                    language = line[len("language="):].strip()
                elif line.startswith("filectx="):
                    value = line[len("filectx="):].strip()
                    if value:
                        try:
                            loaded_paths = json.loads(value)
                            if isinstance(loaded_paths, list):
                                file_context.extend(loaded_paths)
                        except json.JSONDecodeError:
                            pass
    else:
        with open(dataStorage, 'w') as file:
            file.write("API_KEY=\n")
            file.write("maxTokens=200\n")
            file.write("language=\n")
            file.write("filectx=[]\n")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}", 
        "Content-Type": "application/json"
    }

    print("Loaded settings: \n  API_KEY: " + API_KEY + "\n  maxTokens: " + str(maxTokens) + "\n  language: " + language)

def save_settings():
    with open(dataStorage, 'w') as file:
        file.write("API_KEY=" + API_KEY + "\n")
        file.write("maxTokens=" + str(maxTokens) + "\n")
        file.write("language=" + language + "\n")
        file.write("filectx=" + json.dumps(file_context) + "\n")
    load_settings()

#reads files for the context system
def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return content

#makes the request to the ai and returns what the ai spits out
def generate_content(request, language):
    load_ctx()
    data = {
        "model": "deepseek-ai/deepseek-v4-pro",
        "messages": [
            {"role": "user", "content": tokenSaver + " Complete the following request: " + request + " in " + language + "; Context: " + ctxString}
        ],
        "max_tokens": maxTokens
    }

    print("requesting...")
    response = requests.post(url, headers=headers, json=data)

    result = ""

    if response.status_code == 200:
        response_data = response.json()
        generated_content = response_data['choices'][0]['message']['content']
        result = generated_content.strip()
    else:
        startidx = response.text.find("title>") + len("message") + 3
        endidx = response.text.find("</title>")

        result = f"Error{response.text[startidx:endidx]}"
    return result

#recieves content and shows the user what it got aswell as copying it to the clipboard
def query():
    if language == "":
        print("No default programming language set, please specify the language in settings")
        return
    
    if API_KEY == "":
        print("No API key set, please specify your API key in settings")
        return

    request = input("Enter your request: ")

    os.system('cls' if os.name == 'nt' else 'clear')
    result = generate_content(request, language)
    pyperclip.copy(result)

    code_generated_context.append(result)

    print("The Following code has been copied to your clipboard: \n" + result)

#settings menu
def settings():
    initial = input("Enter a setting to go to (enter 'list' for a full list): ")
    while True:
            change = None

            if initial:
                change = initial
                initial = None
            else:
                change = input("Go to setting: ")
            if change == "api_key":
                global API_KEY
                API_KEY = input("Enter your new API key: ")
                print("API key updated successfully to " + API_KEY)
            elif change == "tokensLimit":
                global maxTokens
                maxTokens = int(input("Enter your new tokens limit: "))
                print("Tokens limit updated successfully to " + str(maxTokens))
            elif change == "list":
                print("Available settings: \n   api_key (changes the current api key) \n   tokensLimit (changes the current tokens limit for each response) \n   language (changes the default programming language) \n   back (exits the settings menu)")
            elif change == "back":
                break
            elif change == "language":
                global language
                language = input("Enter your new default programming language: ")
                print("Default programming language updated successfully to " + language)
            else:
                print("Invalid setting")    
    save_settings()

#main function
def main():
    cmd = input("Enter a command (enter cmds for a full list): ")
    if cmd == "exit":
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    elif cmd == "query":
        query()
    elif cmd == "settings":
        settings()
        os.system('cls' if os.name == 'nt' else 'clear')
    elif cmd == "cmds":
        print("Available commands: \n   query (starts a new query) \n   settings (opens the settings menu) \n   context (manages the context) \n   exit (exits the program)")
    elif cmd == "context":
        action=int(input("Would you like to \n 1. Add a file \n 2. Clear ALL context"))
        print(action)
        if action == 1:
            path = input("Enter the file path: ")
            if os.path.isfile(path) and path not in file_context:
                file_context.append(path)
                save_settings()
                load_ctx()
                print("File added to context successfully")
            else:
                print("Invalid file path or file already in context")
        elif action == 2:
            file_context.clear()
            code_generated_context.clear()
            save_settings()
            global ctxString
            ctxString = ""
            print("Context cleared successfully")
    else:
        print("Invalid command '" + cmd + "'")
    main()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    load_settings()
    main()
