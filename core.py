# -*- coding: utf-8 -*-

#TODO: clean up all "print"

# --- Standard library imports (PEP 8) ---
import contextlib
import importlib
import pkgutil

import sys

# --- Third-party library imports (PEP 8) ---
import argparse
from typing import TYPE_CHECKING, cast

# --- Self-hosted library imports (PEP8) ---
from abcd.cli.Argument import verbose_argument
from abcd.cli.commands.AbstractCommand import AbstractCommand
from abcd.__init__ import __version__

#TODO: fix TYPE_CHECKING
# if TYPE_CHECKING:
if True:
    from typing import Any, Iterable

COMMANDS_MODULE_PATH = importlib.import_module("abcd.cli.commands").__path__

"""
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
██ ▄▄▀█ ▄▄▀█ ▄▄ █ ▄▄▀██
██ ▀▀ █ ▄▄▀█ ████ ██ ██
██ ██ █ ▀▀ █ ▀▀ █ ▀▀▄██
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
"""

# ABCD project structure
# ├── modules (e.g. Email, Database, Utils)...
# │   ├── __init__.py
# │   └── some_module.py
# ├── [... all modules modules]
# ├── setup.py (to be added in the future)
# └── bin
#     ├── cli_script (this file, main entry point for CLI
# │   └── [... supporting files for cli]




class Core():
    """Top level object handling the entire CLI interface"""
        # OOPification of argparse. Too much? Who knows...
        # https://www.sobyte.net/post/2022-04/advanced-argparse/
        
        
    parer: argparse.ArgumentParser
    subparsers: argparse._SubParsersAction
    
    def __init__(self) -> None:
        self.version = __version__
        self.commands: list[str] = []
        self.exit_stack = contextlib.ExitStack()        # https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack
        # self.exit_stack.callback(setattr, self, "config_settings", None)
        self.init_parser()
        
    def init_parser(self) -> None:
        """initializes the core parser class"""
        self.parser = argparse.ArgumentParser(
                            prog="ABCD",
                            description="""
                                        ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
                                        ██ ▄▄▀█ ▄▄▀█ ▄▄ █ ▄▄▀██
                                        ██ ▀▀ █ ▄▄▀█ ████ ██ ██
                                        ██ ██ █ ▀▀ █ ▀▀ █ ▀▀▄██
                                        ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                   
                            Affordable Business Contact Directory (ABCD)
                            """,
                            epilog="""
                      ------------------------------------------------------------
                       This package is experimental and should be used carefully.
                      
                                 
                                   Contact Maintainers for support
                                       and report your issues.
                               
                               """,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
        
        self.parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"ABCD, version {self.version}",       #TODO: ABCD shouldn't change, but should be replaced by a dynamic string (mabye)
            help="Shows %(prog)s version and exits.",
        )
        verbose_argument.add_to_parser(self.parser)
        
        
        #imports all commands defined in the cli/commands folder
        #TODO: use a custom ArgumentParser with title-cased help.
        self.subparsers = self.parser.add_subparsers(parser_class=argparse.ArgumentParser, title="commands", metavar="")
        for _, name, _ in pkgutil.iter_modules(COMMANDS_MODULE_PATH):
            module = importlib.import_module(f"abcd.cli.commands.{name}", __name__)
            try:
                cmd = module.Command
            except AttributeError:
                continue
            self.register_command(cmd, cmd.name or name)
            
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        # print("checkpoint: __call__")
        return self.main(*args, **kwargs)
            
    def register_command(self, command: type[AbstractCommand], name: str | None = None) -> None:
        """Register a subcommand to the subparsers,
        with an optional name of the subcommand.

        Args:
            command (Type[ABCD.cli.commands.AbstractCommand.AbstractCommand]):
                The command class to register
            name (str): The name of the subcommand, if not given, `command.name`
                is used
        """
        assert self.subparsers
        self.commands.append(name or command.name or "")
        command.register_to(self.subparsers, name)
        # print(f"done register_command - command: {name}")
    
    @staticmethod
    def get_command(args: list[str]) -> tuple[int, str]:
        """get the command name from the arguments"""
        # print("checkpoint get_command")
        # print(args)
        for i,a in enumerate(args):
            # print(a)
            if a.startswith("-"):
                # this is an argument of a command, not interested
                continue
            else:
                # this is a command, let's return position and name
                return i,a
        return -1,""
            
    
    def _get_cli_args(self, args: list[str]) -> list[str]:
        """returns an iteratable array of arguments from the cli string"""
        # print("checkpoint: _get_cli_args")
        # for a in args:
            # print(f">> {a}")
        # print("chk end")
        (pos, command) = self.get_command(args)
        # print(f"_get_cli_args: {command}")
        # if command:
            # args[pos + 1 : pos + 1] = list(command)
        # print(args)
        return args
        
        
    def handle(self, arguments: argparse.Namespace) -> None:
        """Called before command invocation"""
        
        # print("invoking handle")
        # print(arguments)
        
        #TODO: add verbose control here
        
        command = cast("AbstractCommand | None", getattr(arguments,"command",None))
        
        for callback in getattr(arguments,"callbacks",[]):
            callback(arguments)
            
        if command is None:
            # print("command is None")
            self.parser.print_help()
            sys.exit(0)
        
        command.handle(arguments)
        
        # print(f"done invoking handle")
        
    
    def main(self, args: list[str] | None = None, prog_name: str | None = None, **extra: Any) -> None:
        """The main entry function of core class"""
        if args is None:
            args = []
            
        # note to self. I'd like to do immediately
        # arguments = self.parser.parse_args(args)
        # but this would return arguments as a Namespace type
        # which, by the way, is not iterable. Therefore I'd like to be able
        # to list my commands and iterate them. The following function call
        # turns args into a list, which can be iterated next
        
        args = self._get_cli_args(args)
        
        #TODO: add exception handler
        arguments = self.parser.parse_args(args)
        #TODO: add exception handler
        self.handle(arguments)


def main(args: list[str] | None = None) -> None:
    """The CLI entry point"""
    core = Core()
    with core.exit_stack:
        return core.main(args or sys.argv[1:])
    # input("Press Enter to continue...")

if __name__ == "__main__":
    main()