from typing import Any, Dict, Tuple

import pytest

from givenergy_modbus.model.register import HoldingRegister  # type: ignore  # shut up mypy
from givenergy_modbus.pdu import (
    HeartbeatRequest,
    HeartbeatResponse,
    ModbusRequest,
    ReadHoldingRegistersRequest,
    ReadHoldingRegistersResponse,
    ReadInputRegistersRequest,
    ReadRegistersRequest,
    ReadRegistersResponse,
    WriteHoldingRegisterRequest,
)
from tests import REQUEST_PDU_MESSAGES, RESPONSE_PDU_MESSAGES, _lookup_pdu_class


def test_str():
    """Test we can represent an instance of PDUs nicely."""
    assert str(ReadRegistersRequest(base_register=3, register_count=6)) == (
        "_/ReadRegistersRequest(base_register=3 register_count=6)"
    )
    assert str(ModbusRequest(foo=1)) == "_/ModbusRequest()"
    assert str(ModbusRequest) == "<class 'givenergy_modbus.pdu.ModbusRequest'>"
    assert str(ModbusRequest(foo=1)) == "_/ModbusRequest()"
    assert str(ModbusRequest) == "<class 'givenergy_modbus.pdu.ModbusRequest'>"

    assert str(ReadHoldingRegistersRequest(foo=1)) == (
        "3/ReadHoldingRegistersRequest(base_register=0 register_count=60)"
    )
    assert str(ReadHoldingRegistersRequest) == "<class 'givenergy_modbus.pdu.ReadHoldingRegistersRequest'>"

    assert str(WriteHoldingRegisterRequest(foo=1)) == "6/WriteHoldingRegisterRequest(register=? value=?)"
    assert str(WriteHoldingRegisterRequest) == "<class 'givenergy_modbus.pdu.WriteHoldingRegisterRequest'>"

    assert str(HeartbeatRequest(foo=1)) == "_/HeartbeatRequest(data_adapter_type=0)"
    assert str(HeartbeatRequest) == "<class 'givenergy_modbus.pdu.HeartbeatRequest'>"
    assert str(HeartbeatResponse(foo=1)) == "_/HeartbeatResponse(data_adapter_type=0)"
    assert str(HeartbeatResponse) == "<class 'givenergy_modbus.pdu.HeartbeatResponse'>"

    assert len(REQUEST_PDU_MESSAGES) == 6
    pdu = _lookup_pdu_class(REQUEST_PDU_MESSAGES[0][0])(**REQUEST_PDU_MESSAGES[0][1])
    assert str(pdu) == '4/ReadInputRegistersRequest(base_register=16 register_count=6)'
    pdu = _lookup_pdu_class(REQUEST_PDU_MESSAGES[1][0])(**REQUEST_PDU_MESSAGES[1][1])
    assert str(pdu) == '3/ReadHoldingRegistersRequest(base_register=20817 register_count=2000)'
    pdu = _lookup_pdu_class(REQUEST_PDU_MESSAGES[2][0])(**REQUEST_PDU_MESSAGES[2][1])
    assert str(pdu) == '3/ReadHoldingRegistersRequest(base_register=20817 register_count=2000)'
    pdu = _lookup_pdu_class(REQUEST_PDU_MESSAGES[3][0])(**REQUEST_PDU_MESSAGES[3][1])
    assert str(pdu) == '6/WriteHoldingRegisterRequest(register=20817 value=2000)'
    pdu = _lookup_pdu_class(REQUEST_PDU_MESSAGES[4][0])(**REQUEST_PDU_MESSAGES[4][1])
    assert str(pdu) == '6/WriteHoldingRegisterRequest(register=20 value=1)'
    pdu = _lookup_pdu_class(REQUEST_PDU_MESSAGES[5][0])(**REQUEST_PDU_MESSAGES[5][1])
    assert str(pdu) == '_/HeartbeatRequest(data_adapter_type=1)'

    assert len(RESPONSE_PDU_MESSAGES) == 4
    pdu = _lookup_pdu_class(RESPONSE_PDU_MESSAGES[0][0])(**RESPONSE_PDU_MESSAGES[0][1])
    assert str(pdu) == '4/ReadInputRegistersResponse(slave_address=0x32 base_register=0 register_count=60)'
    pdu = _lookup_pdu_class(RESPONSE_PDU_MESSAGES[1][0])(**RESPONSE_PDU_MESSAGES[1][1])
    assert str(pdu) == '3/ReadHoldingRegistersResponse(slave_address=0x32 base_register=0 register_count=60)'
    pdu = _lookup_pdu_class(RESPONSE_PDU_MESSAGES[2][0])(**RESPONSE_PDU_MESSAGES[2][1])
    assert str(pdu) == '6/WriteHoldingRegisterResponse(slave_address=0x32 register=35 value=8764)'
    pdu = _lookup_pdu_class(RESPONSE_PDU_MESSAGES[3][0])(**RESPONSE_PDU_MESSAGES[3][1])
    assert str(pdu) == '_/HeartbeatResponse(data_adapter_type=32)'


def test_class_equivalence():
    """Confirm some behaviours on subclassing."""
    assert issubclass(ReadHoldingRegistersRequest, ReadRegistersRequest)
    assert issubclass(ReadInputRegistersRequest, ReadRegistersRequest)
    assert not issubclass(ReadHoldingRegistersRequest, ReadInputRegistersRequest)
    assert isinstance(ReadHoldingRegistersRequest(), ReadRegistersRequest)
    assert isinstance(ReadInputRegistersRequest(), ReadRegistersRequest)
    assert not isinstance(ReadInputRegistersRequest(), ReadHoldingRegistersRequest)
    assert ReadInputRegistersRequest is ReadInputRegistersRequest


def test_cannot_change_function_code():
    """Prevent (accidentally) changing the function_code via kwargs in the constructor."""
    assert ModbusRequest()
    assert ReadHoldingRegistersRequest(function_code=3)

    with pytest.raises(ValueError) as e:
        ModbusRequest(function_code=12)
    assert e.value.args[0] == (
        "Class ModbusRequest does not have a function code, trying to override it is not supported"
    )

    with pytest.raises(ValueError) as e:
        ReadRegistersRequest(function_code=12, base_register=3, register_count=6)
    assert e.value.args[0] == (
        "Class ReadRegistersRequest does not have a function code, trying to override it is not supported"
    )

    with pytest.raises(ValueError) as e:
        assert ReadHoldingRegistersRequest(function_code=14)
    assert e.value.args[0] == (
        "Specified function code 14 is different from what 3/ReadHoldingRegistersRequest() is expecting."
    )


@pytest.mark.parametrize("data", REQUEST_PDU_MESSAGES)
def test_request_pdu_encoding(data: Tuple[str, Dict[str, Any], bytes, bytes, Exception]):
    """Ensure we correctly encode unencapsulated Request messages."""
    pdu_fn, pdu_fn_kwargs, mbap_head, encoded_pdu, ex = data

    pdu: ReadRegistersRequest = _lookup_pdu_class(pdu_fn)(**pdu_fn_kwargs)
    if ex:
        with pytest.raises(ex.__class__) as e:
            pdu.encode()
        assert e.value.args == (ex.args[0], pdu)
    else:
        assert pdu.encode() == encoded_pdu


@pytest.mark.parametrize("data", REQUEST_PDU_MESSAGES)
def test_request_pdu_decoding(data: Tuple[str, Dict[str, Any], bytes, bytes, Exception]):
    """Ensure we correctly decode Request messages to their unencapsulated PDU."""
    pdu_fn, pdu_fn_kwargs, mbap_head, encoded_pdu, ex = data

    pdu: ReadRegistersRequest = _lookup_pdu_class(pdu_fn)()
    if ex:
        with pytest.raises(ex.__class__) as e:
            pdu.decode(encoded_pdu)
        assert e.value.args == (ex.args[0], pdu)
    else:
        pdu.decode(encoded_pdu)
        if pdu_fn_kwargs:
            i = 0
            for (arg, val) in pdu_fn_kwargs.items():
                i += 1
                assert getattr(pdu, arg) == val, f'test {i}: "{arg}" value was not decoded/stored correctly'
            assert i == len(pdu_fn_kwargs.keys())
            assert i > 0


@pytest.mark.parametrize("data", RESPONSE_PDU_MESSAGES)
def test_response_pdu_encoding(data: Tuple[str, Dict[str, Any], bytes, bytes]):
    """Ensure we correctly encode unencapsulated Response messages."""
    pdu_fn, pdu_fn_kwargs, _, encoded_pdu = data

    pdu: ReadRegistersResponse = _lookup_pdu_class(pdu_fn)(**pdu_fn_kwargs)
    assert pdu.encode() == encoded_pdu


@pytest.mark.parametrize("data", RESPONSE_PDU_MESSAGES)
def test_response_pdu_decoding(data: Tuple[str, Dict[str, Any], bytes, bytes]):
    """Ensure we correctly decode Response messages to their unencapsulated PDU."""
    pdu_fn, pdu_fn_kwargs, mbap_header, encoded_pdu = data

    pdu: ReadRegistersResponse = _lookup_pdu_class(pdu_fn)()
    pdu.decode(encoded_pdu)
    if pdu_fn_kwargs:
        i = 0
        for (arg, val) in pdu_fn_kwargs.items():
            i += 1
            assert getattr(pdu, arg) == val, f'test {i}: "{arg}" value was not decoded/stored correctly'
        assert i == len(pdu_fn_kwargs.keys())
        assert i > 0


def test_writable_registers_match():
    """Ensure HoldingRegisters declared write-safe match the WriteHoldingRegisterRequest allow list."""
    write_safe_holding_registers = set()
    for r in HoldingRegister.__members__.values():
        if r.write_safe:
            write_safe_holding_registers.add(r.value)

    assert WriteHoldingRegisterRequest.writable_registers == write_safe_holding_registers


def test_read_registers_response_as_dict():
    """Ensure a ReadRegistersResponse can be turned into a dict representation."""
    r = ReadHoldingRegistersResponse(base_register=100, register_count=10, register_values=list(range(10))[::-1])
    assert r.to_dict() == {100: 9, 101: 8, 102: 7, 103: 6, 104: 5, 105: 4, 106: 3, 107: 2, 108: 1, 109: 0}

    r = ReadHoldingRegistersResponse(base_register=1000, register_count=10, register_values=['a'] * 10)
    assert r.to_dict() == {
        1000: 'a',
        1001: 'a',
        1002: 'a',
        1003: 'a',
        1004: 'a',
        1005: 'a',
        1006: 'a',
        1007: 'a',
        1008: 'a',
        1009: 'a',
    }
