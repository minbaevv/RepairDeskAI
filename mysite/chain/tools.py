import json

from langchain_core.tools import tool
from pydantic import ValidationError

from mysite.chain.validation import InputRejected, input_chain
from mysite.database.services import (
    RequestNotFound,
    create_request,
    list_requests,
    update_request,
)
from mysite.schemas.repair import RepairCreate, RepairStatus, RepairUpdate


def encode(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)


@tool
def request_create(client_name: str, device: str, problem: str) -> str:
    """Создать заявку на ремонт. Нужны имя клиента, устройство и описание проблемы."""
    try:
        data = RepairCreate(
            client_name=input_chain.invoke(client_name),
            device=input_chain.invoke(device),
            problem=input_chain.invoke(problem),
        )
        return encode({"ok": True, "request": create_request(data)})
    except (ValidationError, InputRejected) as error:
        return encode({"ok": False, "error": str(error)})


@tool
def request_update(
    request_id: int,
    status: RepairStatus | None = None,
    problem: str | None = None,
) -> str:
    """Обновить статус или описание заявки по id. Статусы: new, in_progress, done, cancelled."""
    try:
        if request_id < 1:
            return encode({"ok": False, "error": "Некорректный id"})
        data = RepairUpdate(
            status=status,
            problem=input_chain.invoke(problem) if problem is not None else None,
        )
        return encode({"ok": True, "request": update_request(request_id, data)})
    except (ValidationError, InputRejected, RequestNotFound) as error:
        return encode({"ok": False, "error": str(error)})


@tool
def request_list(
    status: RepairStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """Показать заявки и их общее количество. Можно указать статус, limit и offset."""
    if not 1 <= limit <= 100 or offset < 0:
        return encode({"ok": False, "error": "limit: 1–100, offset: от 0"})
    return encode({"ok": True, **list_requests(status, limit, offset)})
