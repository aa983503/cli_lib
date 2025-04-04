import cli_library

@cli_library.cli_command("hello")
def print_hello_world():
    print("Hello, World!")

@cli_library.cli_command("custom_hello")
def print_custom_hello():
    number = input("Enter a number: ")
    text = input("Enter a string: ")
    print(f"Hello {number} {text}")

@cli_library.cli_command("connect", subcommands={"ip": None, "port": None})
def connect(ip="127.0.0.1", port=1337):
    # ip = input("Enter IP address: ")
    # port = input("Enter port: ")
    print(f"Connecting to {ip}:{port}")

@cli_library.cli_command("copy", subcommands={"source": None, "destination": None, "mode": None})
def copy(source, destination, mode):
    print(f'copying {source} to {destination}, new file mode: {mode}')

if __name__ == "__main__":
    # register_commands returns all of the commands and the default completer we are creating
    commands = cli_library.register_commands(__import__(__name__))
    cli_library.run_cli(commands)
