from typing import Dict, List
from app.core.exceptions import BadRequestError
from ..constants import StatusEnum, SeverityEnum


class TodoPolicy:
    def __init__(self):
        # Status transition rules
        self.allowed_status_transitions: Dict[StatusEnum, List[StatusEnum]] = {
            StatusEnum.TODO: [
                StatusEnum.IN_PROGRESS,
                StatusEnum.DONE,
                StatusEnum.CANCELLED,
            ],
            StatusEnum.IN_PROGRESS: [
                StatusEnum.TODO,
                StatusEnum.DONE,
                StatusEnum.CANCELLED,
            ],
            StatusEnum.CANCELLED: [
                StatusEnum.TODO,
                StatusEnum.IN_PROGRESS,
                StatusEnum.DONE,
            ],
            StatusEnum.DONE: [],  # Cannot transition to any other status
        }

        self.allowed_severity_transitions: Dict[SeverityEnum, List[SeverityEnum]] = {
            SeverityEnum.LOW: [
                SeverityEnum.MEDIUM,
                SeverityEnum.HIGH,
                SeverityEnum.CRITICAL,
            ],
            SeverityEnum.MEDIUM: [
                SeverityEnum.LOW,
                SeverityEnum.HIGH,
                SeverityEnum.CRITICAL,
            ],
            SeverityEnum.HIGH: [
                SeverityEnum.LOW,
                SeverityEnum.MEDIUM,
                SeverityEnum.CRITICAL,
            ],
            SeverityEnum.CRITICAL: [
                SeverityEnum.LOW,
                SeverityEnum.MEDIUM,
                SeverityEnum.HIGH,
            ],
        }

    def validate_status_transition(
        self, current_status: StatusEnum, new_status: StatusEnum
    ) -> None:
        """Validate if the status transition is allowed."""
        if current_status == StatusEnum.DONE:
            raise BadRequestError(
                detail=f"Cannot change status once it is {StatusEnum.DONE.value}"
            )

        if new_status not in self.allowed_status_transitions[current_status]:
            raise BadRequestError(
                detail=f"Cannot transition from {current_status.value} to {new_status.value}"
            )

    def validate_severity_transition(
        self, current_severity: SeverityEnum, new_severity: SeverityEnum
    ) -> None:
        """Validate if the severity transition is allowed."""
        if new_severity not in self.allowed_severity_transitions[current_severity]:
            raise BadRequestError(
                detail=f"Cannot transition from {current_severity.value} to {new_severity.value}"
            )
