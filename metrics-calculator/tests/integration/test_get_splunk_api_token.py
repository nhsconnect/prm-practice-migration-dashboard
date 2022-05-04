import boto3
import os
import pytest

from moto import mock_ssm
from chalicelib.get_splunk_api_token import get_splunk_api_token


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def ssm(aws_credentials):
    with mock_ssm():
        yield boto3.client('ssm', region_name='us-east-1')


def test_get_splunk_api_token_returns_api_token(ssm):
    expected_token_value = "this-is-a-token"
    parameter_name = "Splunk API token"
    ssm.put_parameter(
        Name=parameter_name,
        KeyId="custom-key-id",
        Value=expected_token_value, Type="SecureString")

    returned_token_value = get_splunk_api_token(ssm, parameter_name)

    assert returned_token_value == expected_token_value
