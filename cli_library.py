from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter

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
    completer_dict = {}
    for name in dir(module):
        obj = getattr(module, name)
        # Essentially saying take all of the functions in our program and if this function has the decorator, add it to our dictionary
        if callable(obj) and hasattr(obj, "_cli_command"):

            # This is just a proof of concept on grabbing the argument to a function
            function_args = obj.__code__.co_varnames[:obj.__code__.co_argcount]
            print(function_args)
            # Store a list of all of the top level commands
            commands[obj._cli_command] = obj
            # Store a dictionary of all of the subcommands registered to the top level command
            completer_dict[obj._cli_command] = obj._cli_subcommands
    # NestedCompleter takes in a dictionary. We are dynamically creating this dict making it super portable. Returns the list of top level commands along with the dynamically created subcommands for tab completion
    return commands, NestedCompleter.from_nested_dict(completer_dict)

def run_cli(commands, completer):
    """Runs a simple CLI using prompt_toolkit with enforced subcommands."""
    # Begin the cli loop
    while True:
        try:
            user_input = prompt("cli> ", completer=completer)
            parts = user_input.split()
            if not parts:
                continue
            
            # grab the top level command and verify that it is a registered command
            command = parts[0]
            if command in commands:
                # begin parsing the list of subcommands associated with the top level command
                expected_subcommands = commands[command]._cli_subcommands
                # if expected_subcommands and len(parts) < 3:
                #     print(f"Error: Missing subcommands. Expected: {', '.join(expected_subcommands.keys())}")
                #     continue
                commands[command]()
            elif command == "exit":
                break
            else:
                print("Unknown command")
        except KeyboardInterrupt:
            break
