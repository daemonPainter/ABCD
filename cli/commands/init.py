# -*- coding: utf-8 -*-

# --- Standard library imports (PEP 8) ---
from __future__ import annotations
import os

# --- Third-party library imports (PEP 8) ---
import argparse
from typing import TYPE_CHECKING

# --- Self-hosted library imports (PEP8) ---
from abcd.cli.Argument import verbose_argument
from abcd.cli.commands.AbstractCommand import AbstractCommand

# if TYPE_CHECKING:
if True:
    from typing import Collection


class Command(AbstractCommand):
    """Initializes a ABCD workspace"""
    
    arguments = (
        *AbstractCommand.arguments,
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Manipulate the argument parser to add more arguments"""
        parser.add_argument(
            "-f",
            "--force",
            help="Forces initialization of workspace, even if the target directory is already a workspace. Functionally identical to \"delete\" followed by \"init\" with no options.",
            action="store_false",
        )
        
    
    def handle(self, arguments: argparse.Namespace) -> None:
        path = os.path.join(os.getcwd(),".ABCD")
        if(os.path.isdir(path) and not arguments.force):
            print("WARNING: this folder is already a ABCD workspace, init will have no effect")
        else:
            os.mkdir(path)
            