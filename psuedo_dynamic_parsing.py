from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

# Define commands and subcommands
commands = {
    "add": ["name", "description", "priority"],
    "remove": ["id"],
    "list": ["filter"]
}

class StatefulCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands

    def get_completions(self, document, complete_event):
        # Tokenize the input
        tokens = document.text.split()
        
        if len(tokens) == 0:
            # Suggest root commands
            for cmd in self.commands.keys():
                yield Completion(cmd)
        elif len(tokens) == 1:
            # Suggest subcommands for the entered command
            command = tokens[0]
            if command in self.commands:
                for sub in self.commands[command]:
                    yield Completion(sub)
        else:
            # Exclude already entered subcommands
            command = tokens[0]
            entered = set(tokens[1:])  # Subcommands already entered
            if command in self.commands:
                for sub in self.commands[command]:
                    if sub not in entered:
                        yield Completion(sub)

# Instantiate the completer
completer = StatefulCompleter(commands)

# Prompt loop
while True:
    user_input = prompt(">> ", completer=completer)
    print(f"You entered: {user_input}")
