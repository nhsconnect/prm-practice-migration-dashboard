from chalice.test import Client
from src.app import app


def test_calculate_dashboard_metrics_from_telemetry():
    with Client(app) as client:
        result = client.lambda_.invoke(
            'calculate_dashboard_metrics_from_telemetry')

        assert result.payload == "ok"
