from typing import Dict, List
from app.core.exceptions import BadRequestError
from ..constants import TodoStatusEnum, TodoSeverityEnum


class TodoPolicy:
    def __init__(self):
        # Status transition rules
        self.allowed_status_transitions: Dict[TodoStatusEnum, List[TodoStatusEnum]] = {
            TodoStatusEnum.TODO: [
                TodoStatusEnum.IN_PROGRESS,
                TodoStatusEnum.DONE,
                TodoStatusEnum.CANCELLED,
            ],
            TodoStatusEnum.IN_PROGRESS: [
                TodoStatusEnum.TODO,
                TodoStatusEnum.DONE,
                TodoStatusEnum.CANCELLED,
            ],
            TodoStatusEnum.CANCELLED: [
                TodoStatusEnum.TODO,
                TodoStatusEnum.IN_PROGRESS,
                TodoStatusEnum.DONE,
            ],
            TodoStatusEnum.DONE: [],  # Cannot transition to any other status
        }

        self.allowed_severity_transitions: Dict[
            TodoSeverityEnum, List[TodoSeverityEnum]
        ] = {
            TodoSeverityEnum.LOW: [
                TodoSeverityEnum.MEDIUM,
                TodoSeverityEnum.HIGH,
                TodoSeverityEnum.CRITICAL,
            ],
            TodoSeverityEnum.MEDIUM: [
                TodoSeverityEnum.LOW,
                TodoSeverityEnum.HIGH,
                TodoSeverityEnum.CRITICAL,
            ],
            TodoSeverityEnum.HIGH: [
                TodoSeverityEnum.LOW,
                TodoSeverityEnum.MEDIUM,
                TodoSeverityEnum.CRITICAL,
            ],
            TodoSeverityEnum.CRITICAL: [
                TodoSeverityEnum.LOW,
                TodoSeverityEnum.MEDIUM,
                TodoSeverityEnum.HIGH,
            ],
        }

    def validate_status_transition(
        self, current_status: TodoStatusEnum, new_status: TodoStatusEnum
    ) -> None:
        """Validate if the status transition is allowed."""
        if current_status == TodoStatusEnum.DONE:
            raise BadRequestError(
                detail=f"Cannot change status once it is {TodoStatusEnum.DONE.value}"
            )

        if new_status not in self.allowed_status_transitions[current_status]:
            raise BadRequestError(
                detail=f"Cannot transition from {current_status.value} to {new_status.value}"
            )

    def validate_severity_transition(
        self, current_severity: TodoSeverityEnum, new_severity: TodoSeverityEnum
    ) -> None:
        """Validate if the severity transition is allowed."""
        if new_severity not in self.allowed_severity_transitions[current_severity]:
            raise BadRequestError(
                detail=f"Cannot transition from {current_severity.value} to {new_severity.value}"
            )
