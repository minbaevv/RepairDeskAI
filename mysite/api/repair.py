from fastapi import APIRouter, HTTPException, Query

from mysite.chain.validation import input_chain
from mysite.database.services import (
    RequestNotFound,
    create_request,
    list_requests,
    update_request,
)
from mysite.schemas.repair import (
    RepairCreate,
    RepairList,
    RepairRead,
    RepairStatus,
    RepairUpdate,
)

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post("", response_model=RepairRead, status_code=201)
def create(data: RepairCreate):
    for value in data.model_dump().values():
        input_chain.invoke(value)
    return create_request(data)


@router.patch("/{request_id}", response_model=RepairRead)
def update(request_id: int, data: RepairUpdate):
    if request_id < 1:
        raise HTTPException(status_code=422, detail="Некорректный id")
    if data.problem is not None:
        input_chain.invoke(data.problem)
    try:
        return update_request(request_id, data)
    except RequestNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("", response_model=RepairList)
def list_all(
    status: RepairStatus | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return list_requests(status, limit, offset)
