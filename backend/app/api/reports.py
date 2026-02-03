from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

if False:
    from app.models.user import User

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.report import ReportResponse
from app.services.report_generator import ReportGeneratorService
from app.services.llm_orchestrator import LLMOrchestrator


router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific report"""
    service = ReportGeneratorService(db, LLMOrchestrator())

    # Get report and verify user owns the discussion
    from app.models.report import Report
    from app.models.discussion import Discussion
    from sqlalchemy import select

    result = await db.execute(
        select(Report).join(Discussion).where(
            Report.id == report_id,
            Discussion.user_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return ReportResponse.model_validate(report)


@router.get("/discussions/{discussion_id}", response_model=ReportResponse)
async def get_discussion_report(
    discussion_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get or generate report for a discussion"""
    service = ReportGeneratorService(db, LLMOrchestrator())

    # Try to get existing report
    from app.models.report import Report
    from app.models.discussion import Discussion
    from sqlalchemy import select

    result = await db.execute(
        select(Report).join(Discussion).where(
            Report.discussion_id == discussion_id,
            Discussion.user_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if report:
        return ReportResponse.model_validate(report)

    # If no report exists, generate it
    try:
        report = await service.generate_report(discussion_id)
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/discussions/{discussion_id}/regenerate", response_model=ReportResponse)
async def regenerate_report(
    discussion_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Regenerate report for a discussion"""
    service = ReportGeneratorService(db, LLMOrchestrator())

    # Verify user owns the discussion
    from app.models.discussion import Discussion
    from sqlalchemy import select

    result = await db.execute(
        select(Discussion).where(
            Discussion.id == discussion_id,
            Discussion.user_id == current_user.id
        )
    )
    discussion = result.scalar_one_or_none()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    if discussion.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discussion must be completed to generate report"
        )

    try:
        report = await service.generate_report(discussion_id)
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
