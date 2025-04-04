from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion


class CustomCompleter(Completer):
    def __init__(self, commands):
        """
        Initialize the custom completer with a dictionary of commands and their subcommands.
        :param commands: A dictionary where keys are top-level commands and values are subcommand dictionaries.
        """
        self.commands = commands

    def get_completions(self, document, complete_event):
        # Tokenize the input
        tokens = document.text.split()

        if len(tokens) == 0:
            # Suggest root commands
            for cmd in self.commands.keys():
                yield Completion(cmd)
        else:
            # Exclude already entered subcommands
            command = tokens[0]
            entered = set(tokens[1:])  # Subcommands already entered

            if command in self.commands:
                for sub in self.commands[command]:
                    last_token = tokens[-1]
                    partials = [
                        x
                        for x in self.commands.keys()
                        if x.startswith(last_token) and last_token != command
                    ]

                    if len(partials) > 0:
                        for sub in partials:
                            yield Completion(sub)
                    elif sub not in entered:
                        yield Completion(sub)
            else:
                command = tokens[-1]
                for sub in (x for x in self.commands.keys() if x.startswith(command)):
                    yield Completion(sub)

    def get_keys(self):
        return self.commands.keys()


# this set up the structure of the decorator for what we expect the developer to write
def cli_command(command_name, subcommands=None):
    def decorator(func):
        func._cli_command = command_name
        func._cli_subcommands = (
            subcommands or {}
        )  # Store subcommand structure associated with the command
        return func

    return decorator


def register_commands(module):
    """Finds and registers functions with the @cli_command decorator and sets up tab completion."""
    commands = {}
    completer_dict = {}
    for name in dir(module):
        obj = getattr(module, name)
        # Essentially saying take all of the functions in our program and if this function has the decorator, add it to our dictionary
        if callable(obj) and hasattr(obj, "_cli_command"):

            # This is just a proof of concept on grabbing the argument to a function
            function_args = obj.__code__.co_varnames[: obj.__code__.co_argcount]
            # Store a list of all of the top level commands
            commands[obj._cli_command] = obj
            # Store a dictionary of all of the subcommands registered to the top level command
            completer_dict[obj._cli_command] = obj._cli_subcommands

            print(completer_dict)

    # NestedCompleter takes in a dictionary. We are dynamically creating this dict making it super portable. Returns the list of top level commands along with the dynamically created subcommands for tab completion
    return commands, CustomCompleter(completer_dict)


def run_cli(commands, completer):
    # def run_cli(completer):
    """Runs a simple CLI using prompt_toolkit with enforced subcommands."""
    # Begin the cli loop
    session = PromptSession()
    while True:
        try:
            user_input = session.prompt(
                "cli> ", completer=completer, auto_suggest=AutoSuggestFromHistory()
            )

            parts = user_input.split()
            if not parts:
                continue

            # grab the top level command and verify that it is a registered command
            command = parts[0]
            if command in completer.get_keys():
                # begin parsing the list of subcommands associated with the top level command
                # expected_subcommands = commands[command]._cli_subcommands
                # if expected_subcommands and len(parts) < 3:
                #     print(f"Error: Missing subcommands. Expected: {', '.join(expected_subcommands.keys())}")
                #     continue
                # commands[command]()
                print("Executing command:", user_input)
            elif command == "exit":
                break
            else:
                print("Unknown command")
        except KeyboardInterrupt:
            break
