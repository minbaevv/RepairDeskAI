from sqlalchemy import func, select

from mysite.database.db import SessionLocal
from mysite.database.models import RepairRequest
from mysite.schemas.repair import RepairCreate, RepairRead, RepairUpdate


class RequestNotFound(ValueError):
    pass


def create_request(data: RepairCreate) -> dict:
    with SessionLocal() as db:
        request = RepairRequest(**data.model_dump())
        db.add(request)
        db.commit()
        db.refresh(request)
        return RepairRead.model_validate(request).model_dump(mode="json")


def update_request(request_id: int, data: RepairUpdate) -> dict:
    with SessionLocal() as db:
        request = db.get(RepairRequest, request_id)
        if request is None:
            raise RequestNotFound("Заявка не найдена")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(request, field, value)
        db.commit()
        db.refresh(request)
        return RepairRead.model_validate(request).model_dump(mode="json")


def list_requests(status: str | None, limit: int, offset: int) -> dict:
    with SessionLocal() as db:
        query = select(RepairRequest)
        total = select(func.count()).select_from(RepairRequest)
        if status is not None:
            query = query.where(RepairRequest.status == status)
            total = total.where(RepairRequest.status == status)
        requests = db.scalars(
            query.order_by(RepairRequest.id.desc()).offset(offset).limit(limit)
        ).all()
        return {
            "count": db.scalar(total),
            "items": [
                RepairRead.model_validate(request).model_dump(mode="json")
                for request in requests
            ],
        }
