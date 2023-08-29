"""Module containing the code for the Variable and Domain classes."""

def check_if_compiled() -> bool:
    """Check if this code has been compiled with Cython.

    Returns:
        bool: whether the code has been compiled.
    """
    from cython import compiled

    return compiled

# ----------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------


class Variable(object):
    """Helper class for variable definition.

    Using this class is optional, since any hashable object,
    including plain strings and integers, may be used as variables.
    """

    def __init__(self, name):
        """Initialization method.

        Args:
            name (string): Generic variable name for problem-specific
                purposes
        """
        self.name = name

    def __repr__(self):
        """Represents itself with the name attribute."""
        return self.name


Unassigned = Variable("Unassigned")  #: Helper object instance representing unassigned values


# ----------------------------------------------------------------------
# Domains
# ----------------------------------------------------------------------


class Domain(list):
    """Class used to control possible values for variables.

    When list or tuples are used as domains, they are automatically
    converted to an instance of that class.
    """

    def __init__(self, set):
        """Initialization method.

        Args:
            set: Set of values, comparable by equality, that the given variables may assume.
        """
        list.__init__(self, set)
        self._hidden = []
        self._states = []

    def resetState(self):
        """Reset to the original domain state, including all possible values."""
        self.extend(self._hidden)
        del self._hidden[:]
        del self._states[:]

    def pushState(self):
        """Save current domain state.

        Variables hidden after that call are restored when that state is popped from the stack.
        """
        self._states.append(len(self))

    def popState(self):
        """Restore domain state from the top of the stack.

        Variables hidden since the last popped state are then available again.
        """
        diff = self._states.pop() - len(self)
        if diff:
            self.extend(self._hidden[-diff:])
            del self._hidden[-diff:]

    def hideValue(self, value):
        """Hide the given value from the domain.

        After that call the given value won't be seen as a possible value on that domain anymore.
        The hidden value will be restored when the previous saved state is popped.

        Args:
            value: Object currently available in the domain
        """
        list.remove(self, value)
        self._hidden.append(value)
