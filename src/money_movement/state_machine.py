from typing import Dict, List, TypeVar, Generic
from enum import Enum

# Define a type variable that must be an instance of Enum
T = TypeVar("T", bound=Enum)


class GenericStateMachine(Generic[T]):

    transitions: Dict[T, List[T]] = {}

    def __init__(self, initial_state: T | None = None):
        self.state = initial_state

    def set_initial_state(self, initial_state: T):
        if not self.state:
            self.state = initial_state
        else:
            raise ValueError("Initial state already set")

    def can_transition(self, new_state: T) -> bool:
        return new_state in self.transitions[self.state]

    def transition(self, new_state: T):
        if self.can_transition(new_state):
            print(f"Transitioning from {self.state.name} to {new_state.name}")
            self.state = new_state
        else:
            raise ValueError(
                f"Invalid transition from {self.state.name} to {new_state.name}"
            )

    def get_state(self) -> T:
        return self.state
