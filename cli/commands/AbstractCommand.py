# -*- coding: utf-8 -*-

# --- Standard library imports (PEP 8) ---
from abc import ABC, abstractmethod

# --- Third-party library imports (PEP 8) ---
import argparse
from argparse import _SubParsersAction
from typing import Any, Sequence, TypeVar

# --- Self-hosted library imports (PEP8) ---
from abcd.cli.Argument import Argument, verbose_argument


C = TypeVar("C", bound="Command")

class AbstractCommand:
    """Abstract definition of a CLI Command.
    
        Each Command is created with the base set of argument defined in
        arguments. Subclasses may ovveride this Property.
    """
    
    # Command name
    name: str | None = None
    # Command's help string, if not given __doc__ is used
    description: str | None = None
    # List of pre-defined options. Override if you wish to customize
    arguments: Sequence[Argument] = (verbose_argument,)     # comma at the end, or more than one item, otherwise not recognized as iteratable and fails
    
    
    # see original: https://github.com/pdm-project/pdm/blob/main/src/pdm/cli/commands/base.py
    @classmethod
    def init_parser(cls: type[C], parser: argparse.ArgumentParser) -> C:
        cmd = cls()
        for arg in cmd.arguments:
            arg.add_to_parser(parser)
        cmd.add_arguments(parser)
        return cmd
        
    @classmethod
    def register_to(cls, subparsers: _SubParsersAction, name: str | None = None, **kwargs: Any) -> None:
        """Register a subcommand to the subparsers,
        with an optional name of the subcommand.
        """
        help_text = cls.description or cls.__doc__
        name = name or cls.name or ""
        # Remove the existing subparser as it will raise an error on Python 3.11+
        subparsers._name_parser_map.pop(name, None)
        subactions = subparsers._get_subactions()
        subactions[:] = [action for action in subactions if action.dest != name]
        parser = subparsers.add_parser(
            name,
            description=help_text,
            help=help_text,
            **kwargs,
        )
        command = cls.init_parser(parser)
        command.name = name
        # Store the command instance in the parsed args. See pdm/core.py for more details
        parser.set_defaults(command=command)
        # print(f"done register_to - command: {name}")
    
    @abstractmethod
    def add_arguments(self, parser):
        """Manipulate the argument parser to add more arguments"""
        pass
        
    @abstractmethod
    def handle(self, arguments: argparse.Namespace) -> None:
        """The command handler function.

        :param arguments: the parsed Namespace object
        """
        raise NotImplementedError