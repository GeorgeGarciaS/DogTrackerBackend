from sqlalchemy.orm import Session

from src.api.schemas.data_quality_issue import DataQualityIssueRequest
from src.db.models.data_quality_issue import DataQualityIssueModel
from src.db.repositories.data_quality_issue_repo import get_data_quality_issue_by_id


def get_data_quality_issue(
    payload: DataQualityIssueRequest,
    db: Session
) -> list[DataQualityIssueModel]:
    event_id = payload.event_id
    data_quality_issue_record = get_data_quality_issue_by_id(event_id, db)
    return data_quality_issue_record
