# -*- coding: utf-8 -*-

# --- Standard library imports (PEP 8) ---
from future import __annotations__

# --- Third-party library imports (PEP 8) ---
import argparse
from typing import TYPE_CHECKING, cast, Any
#TODO: fix TYPE_CHECKING
# if TYPE_CHECKING:
if True:
    from typing import Any, Protocol, Sequence
    
    class ActionCallback(Protocol):
        def __call__(
            self,
            namespace: argparse.Namespace,
            values: Any,
            argument_str: str | None = None,
        ) -> None: ...

# --- Self-hosted library imports (PEP8) ---


class Argument:
    """ Abstract class for a Command argument, delegates all arguments
        to parser.add_argument()
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
    
    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        parser.add_argument(*self.args, **self.kwargs)
        
    def add_to_group(self, group: argparse._ArgumentGroup) -> None:
        group.add_argument(*self.args, **self.kwargs)
        
    def __call__(self, func: ActionCallback):
        self.kwargs.update(action=CallbackAction, callback=func)
        return self

        
class CallbackAction(argparse.Action):
    def __init__(self, *args: Any, callback: ActionCallback, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.callback = callback

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        argument_string: str | None = None,
    ) -> None:
        if not hasattr(namespace, "callbacks"):
            namespace.callbacks = []
        callback = partial(self.callback, values=values, argument_string=argument_string)
        namespace.callbacks.append(callback)


class ArgumentGroup(Argument):
    """A reusable argument group object which can call `add_argument()`
    to add more arguments. And itself will be registered to the parser later.
    """

    def __init__(self, name: str, is_mutually_exclusive: bool = False, required: bool = False) -> None:
        self.name = name
        self.arguments: list[Argument] = []
        self.required = required
        self.is_mutually_exclusive = is_mutually_exclusive

    def add_argument(self, *args: Any, **kwargs: Any) -> None:
        if args and isinstance(args[0], Argument):
            self.arguments.append(args[0])
        else:
            self.arguments.append(Argument(*args, **kwargs))

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        group: argparse._ArgumentGroup
        if self.is_mutually_exclusive:
            group = parser.add_mutually_exclusive_group(required=self.required)
        else:
            group = parser.add_argument_group(self.name)
        for argument in self.arguments:
            argument.add_to_group(group)

    def add_to_group(self, group: argparse._ArgumentGroup) -> None:
        self.add_to_parser(group)
        
verbose_argument = ArgumentGroup("Verbosity options", is_mutually_exclusive=True)
verbose_argument.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Use `-v` for detailed output and `-vv` for more detailed",
)
verbose_argument.add_argument("-q", "--quiet", action="store_const", const=-1, dest="verbose", help="Suppress output")
