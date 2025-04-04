from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion import Completer, Completion

class DynamicCommandCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = text.strip().split()
        word_before_cursor = document.get_word_before_cursor()

        if not parts:
            for cmd in self.commands:
                yield Completion(cmd, start_position=-len(word_before_cursor))
            return

        command = parts[0]

        # Top-level command completion
        if len(parts) == 1 and command not in self.commands:
            for cmd in self.commands:
                if cmd.startswith(command):
                    yield Completion(cmd, start_position=-len(word_before_cursor))
            return

        if command not in self.commands:
            return

        func = self.commands[command]
        subcommands = func._cli_subcommands or {}

        # Track used keys
        provided_keys = set()
        i = 1
        while i < len(parts) - 1:
            key = parts[i]
            if key in subcommands:
                provided_keys.add(key)
                i += 2
            else:
                i += 1

        remaining_keys = {k for k in subcommands if k not in provided_keys}
        prefix = word_before_cursor or ""

        # 🧠 Determine if currently typing a subcommand key
        is_typing_key = (
            len(parts) == 1
            or (len(parts) > 1 and (len(parts) % 2 == 1 or parts[-1] not in subcommands))
        )

        if is_typing_key:
            for key in remaining_keys:
                if key.startswith(prefix):
                    yield Completion(key, start_position=-len(prefix))



# this set up the structure of the decorator for what we expect the developer to write
def cli_command(command_name, subcommands=None):
    def decorator(func):
        func._cli_command = command_name
        func._cli_subcommands = subcommands or {}  # Store subcommand structure associated with the command
        return func
    return decorator

def register_commands(module):
    """Finds and registers functions with the @cli_command decorator and sets up tab completion."""
    commands = {}
    for name in dir(module):
        obj = getattr(module, name)
        # Essentially saying take all of the functions in our program and if this function has the decorator, add it to our dictionary
        if callable(obj) and hasattr(obj, "_cli_command"):

            # This is just a proof of concept on grabbing the argument to a function
            function_args = obj.__code__.co_varnames[:obj.__code__.co_argcount]
            print(function_args)
            # Store a list of all of the top level commands
            commands[obj._cli_command] = obj
    return commands

def run_cli(commands):
    completer = DynamicCommandCompleter(commands)

    while True:
        try:
            user_input = prompt("cli> ", completer=completer)
            parts = user_input.strip().split()
            if not parts:
                continue

            command = parts[0]
            if command == "exit":
                break

            if command in commands:
                func = commands[command]
                subcommands = func._cli_subcommands
                args = {}
                i = 1
                while i < len(parts):
                    key = parts[i]
                    if key in subcommands and i + 1 < len(parts):
                        args[key] = parts[i + 1]
                        i += 2
                    else:
                        print(f"Missing or unknown argument at position {i}: {parts[i]}")
                        break

                if set(args.keys()) == set(subcommands.keys()):
                    func(**args)
                else:
                    print(f"Missing subcommands: {', '.join(set(subcommands) - set(args))}")
            else:
                print("Unknown command")

        except KeyboardInterrupt:
            break


