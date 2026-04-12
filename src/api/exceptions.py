from src.enums import DataQualityIssueErrorType, DogErrorType


class DomainError(Exception):
    def __init__(self, issue: DogErrorType | DataQualityIssueErrorType):
        self.issue = issue
        super().__init__(issue.value)