import json
import pytest
from unittest.mock import Mock
from pydantic.json import pydantic_encoder
from app.modules.device.service import DeviceService
from app.modules.device.schema import DeviceRequest, DeviceResponse
from app.modules.device.model import DeviceModel


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def mock_policy():
    return Mock()


@pytest.fixture
def device_service(mock_repository):
    return DeviceService(repository=mock_repository)


@pytest.fixture
def device_details():
    return {
        "user_id": 1,
        "device_id": "d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1",
        "client_info": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    }


@pytest.fixture
def device_response_data(device_details) -> DeviceResponse:
    return DeviceResponse(
      id=1,
      last_login="2023-08-24T12:00:00.000000",
      **device_details
    )  


@pytest.fixture
def create_request_data(device_details) -> DeviceRequest:
    return DeviceRequest(**device_details)


def dump_data(data):
    return json.dumps(data, sort_keys=True, default=pydantic_encoder)


def extract_device_dict(device: DeviceModel):
    return {
        "user_id": device.user_id,
        "device_id": device.device_id,
        "client_info": device.client_info,
    }


def test_create(device_service, mock_repository, device_response_data, create_request_data):
    # mock repository return value
    mock_repository.create.return_value = device_response_data

    # call the service method
    result = device_service.create(create_request_data)

    # assertions
    mock_repository.create.assert_called_once()

    # check id
    assert result.user_id == 1

    #compare relevant attributes
    result_dict = {
        "user_id": 1,
        "device_id": "d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1",
        "client_info": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    create_data_dict = create_request_data.model_dump(exclude={"id", "last_login"})

    #compare dictionaries
    assert dump_data(result_dict) == dump_data(create_data_dict)


def test_get_by_id(device_service, mock_repository, device_response_data):
    # mock repository return value
    mock_repository.get.return_value = device_response_data
    
    # call the service method
    result = device_service.get(1)

    mock_repository.get.assert_called_once()
    
    # check id
    assert result.id == 1
    assert result.user_id == 1
    assert result.device_id == "d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1"
    assert result.client_info == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def test_delete_device(device_service, mock_repository):
    # mock repository return value
    mock_repository.delete.return_value = True
    # call the service method
    result = device_service.delete(1)
    # assertions
    mock_repository.delete.assert_called_once()
    assert result is True


def test_delete_device_not_found(device_service, mock_repository):
    # mock repository return value
    mock_repository.delete.return_value = False
    # call the service method
    result = device_service.delete(-1)
    # assertions
    mock_repository.delete.assert_called_once()
    assert result is False