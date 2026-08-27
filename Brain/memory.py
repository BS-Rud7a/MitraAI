import json

MEMORY_FILE = "Brain/memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "user_name": "",
            "facts": []
        }


def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def add_memory(fact):
    memory = load_memory()
    memory["facts"].append(fact)
    save_memory(memory)


