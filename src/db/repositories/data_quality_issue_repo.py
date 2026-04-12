from sqlalchemy.orm import Session

from src.db.models.data_quality_issue import DataQualityIssueModel


def get_data_quality_issue_by_id(
    event_id: str,
    db: Session
) -> list[DataQualityIssueModel]:
    return db.query(DataQualityIssueModel).filter(
        DataQualityIssueModel.event_id == event_id
    ).order_by(DataQualityIssueModel.created_at.desc()).all()


