from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.exceptions import DomainError
from src.api.schemas.data_quality_issue import (
    DataQualityIssueRequest,
    DataQualityIssueResponse,
)
from src.db.session import get_db
from src.services.data_quality_issue_service import get_data_quality_issue

router = APIRouter(prefix="/internal/data_quality_issues", tags=["dogs"])


@router.get(
    "/{event_id}",
    response_model=list[DataQualityIssueResponse],
    summary="Get Data Quality Issue Report",
    description="Retrieve a Data quality issue based on a telememrty event id.",
)
def get_data_quality_issue_route(
    event_id: str,
    db: Session = Depends(get_db)
) -> list[DataQualityIssueResponse]:
    try:
        payload = DataQualityIssueRequest(event_id=event_id)
        data_quality_issues = get_data_quality_issue(payload, db)
        print("$$33")
        return [
            DataQualityIssueResponse.model_validate(data_quality_issue)
            for data_quality_issue in data_quality_issues
        ]
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.issue.value)

