
import pytest
from money_movement.util import GenericStateMachine


class SampleState(Enum):
    INITIATED = 1
    COMPLETED = 2
    FAILED = 3

class SampleStateMachine(GenericStateMachine[SampleState]):
    def __init__(self):
        self.state = SampleState.INITIATED
        self.transitions = {
            SampleState.INITIATED: [SampleState.COMPLETED, SampleState.FAILED],
            SampleState.COMPLETED: [],
            SampleState.FAILED: []
        }

class TestGenericStateMachine:
    
    def test_sample_state_machine(self):
        # Create a new state machine
        state_machine = SampleStateMachine()

        # Set the initial state
        state_machine.set_initial_state(SampleState.INITIATED)

        # Check the current state
        assert state_machine.current_state == SampleState.INITIATED

        # Check the current state transitions
        assert state_machine

    def test_fails_transition(self):
        # Create a new state machine
        state_machine = SampleStateMachine()

        # Set the initial state
        state_machine.set_initial_state(SampleState.FAILED)

        # Try to transition to an invalid state
        with pytest.raises(ValueError):
            state_machine.transition(SampleState.INITIATED)