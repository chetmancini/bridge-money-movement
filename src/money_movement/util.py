
from enum import Enum
from typing import Dict, Generic, List, TypeVar
# Define a type variable that must be an instance of Enum
T = TypeVar('T', bound=Enum)

class GenericStateMachine(Generic[T]):
    def __init__(self, initial_state: T, transitions: Dict[T, List[T]]):
        self.state = initial_state
        self.transitions = transitions

    def can_transition(self, new_state: T) -> bool:
        return new_state in self.transitions[self.state]

    def transition(self, new_state: T):
        if self.can_transition(new_state):
            print(f"Transitioning from {self.state.name} to {new_state.name}")
            self.state = new_state
        else:
            raise ValueError(f"Invalid transition from {self.state.name} to {new_state.name}")

    def get_state(self) -> T:
        return self.state