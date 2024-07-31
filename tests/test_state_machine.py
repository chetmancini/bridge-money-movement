from enum import Enum
import pytest
from money_movement.state_machine import GenericStateMachine


class SampleState(Enum):
    INITIATED = 1
    COMPLETED = 2
    FAILED = 3


class SampleStateMachine(GenericStateMachine[SampleState]):
    transitions = {
        SampleState.INITIATED: [SampleState.COMPLETED, SampleState.FAILED],
        SampleState.COMPLETED: [],
        SampleState.FAILED: [],
    }

    def __init__(self, initial_state: SampleState = SampleState.INITIATED):
        self.state = initial_state


class TestGenericStateMachine:
    def test_sample_state_machine_init(self):
        # Create a new state machine
        state_machine = SampleStateMachine(initial_state=SampleState.INITIATED)
        assert state_machine
        assert SampleState.INITIATED == state_machine.get_state()

    def test_sample_state_machine_transition(self):
        # Create a new state machine
        state_machine = SampleStateMachine(initial_state=SampleState.INITIATED)
        state_machine.transition(SampleState.COMPLETED)
        assert SampleState.COMPLETED == state_machine.get_state()

    def test_fails_transition(self):
        # Create a new state machine
        state_machine = SampleStateMachine(initial_state=SampleState.FAILED)

        # Try to transition to an invalid state
        with pytest.raises(ValueError):
            state_machine.transition(SampleState.INITIATED)
