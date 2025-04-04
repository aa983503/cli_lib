import inspect
import argparse

class BuildParser:
    parser = {}
    def build_parser(self, commands):
        """Builds the parser from the command dictionaries provided"""

        #subparsers = parser.add_subparsers(dest="command", help="Subcommands")

        for command in commands:
            parser = argparse.ArgumentParser(description=command)
            signature = inspect.signature(commands[command])
            for name, param in signature.parameters.items():
                parser.add_argument(f"--{name}", type=param.annotation, default=param.default, help="TODO: How do we populate this?")
            self.parser[command] = parser