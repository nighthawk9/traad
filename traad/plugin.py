import itertools

from .compat import getargspec
from .rope.workspace import Workspace
from .state import State


class TraadPlugin:
    """Bottle plugin that manages Workspace, State, and Task-IDs context for traad.

    If this plugin is active, it passes a `Context` object to the `context`
    keyword on handlers. This object has three members:

     - workspace: A `traad.rope.Workspace`
     - state: A `traad.state.State`
     - task_ids: An iterable from which new task IDs can be fetched

    """
    name = 'traad'
    api = 2

    class Context:
        def __init__(self, path):
            self.workspace = Workspace.start(path).proxy()
            self.state = State.start().proxy()
            self.task_ids = itertools.count()

    def __init__(self, root_project_path, keyword='context'):
        self.context = TraadPlugin.Context(root_project_path)
        self.keyword = keyword

    def apply(self, callback, context):
        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = getargspec(context.callback)[0]
        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            kwargs[self.keyword] = self.context
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper

    def close(self):
        self.context.state.stop()
        self.context.workspace.stop()
