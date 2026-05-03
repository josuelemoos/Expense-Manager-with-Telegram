import asyncio
import json
from decimal import Decimal
from typing import cast

import pytest
from fastapi import Request
from pydantic import ValidationError as PydanticValidationError

from app.main import handle_service_error
from app.schemas.reserve import ReserveCreate
from app.schemas.transaction import TransactionCreate
from app.services.exceptions import ValidationError


def test_transaction_description_is_trimmed() -> None:
    payload = TransactionCreate(
        type="expense",
        amount=Decimal("10.00"),
        description="  Mercado  ",
    )

    assert payload.description == "Mercado"


def test_transaction_rejects_blank_description() -> None:
    with pytest.raises(PydanticValidationError):
        TransactionCreate(
            type="expense",
            amount=Decimal("10.00"),
            description="   ",
        )


def test_reserve_rejects_blank_name() -> None:
    with pytest.raises(PydanticValidationError):
        ReserveCreate(name="   ")


def test_global_service_error_handler_shape() -> None:
    response = asyncio.run(
        handle_service_error(
            cast(Request, None),
            ValidationError("Saldo insuficiente."),
        ),
    )

    assert response.status_code == 400
    assert json.loads(response.body) == {"detail": "Saldo insuficiente."}
