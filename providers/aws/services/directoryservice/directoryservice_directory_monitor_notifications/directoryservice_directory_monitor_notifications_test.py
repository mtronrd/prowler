from datetime import datetime
from unittest import mock

from moto.core import DEFAULT_ACCOUNT_ID

from providers.aws.services.directoryservice.directoryservice_service import (
    Directory,
    EventTopics,
    EventTopicStatus,
)

AWS_REGION = "eu-west-1"


class Test_directoryservice_directory_monitor_notifications:
    def test_no_directories(self):
        directoryservice_client = mock.MagicMock
        directoryservice_client.directories = {}
        with mock.patch(
            "providers.aws.services.directoryservice.directoryservice_service.DirectoryService",
            new=directoryservice_client,
        ):
            # Test Check
            from providers.aws.services.directoryservice.directoryservice_directory_monitor_notifications.directoryservice_directory_monitor_notifications import (
                directoryservice_directory_monitor_notifications,
            )

            check = directoryservice_directory_monitor_notifications()
            result = check.execute()

            assert len(result) == 0

    def test_one_directory_logging_disabled(self):
        directoryservice_client = mock.MagicMock
        directory_name = "test-directory"
        directoryservice_client.directories = {
            directory_name: Directory(
                name=directory_name,
                region=AWS_REGION,
                event_topics=[],
            )
        }
        with mock.patch(
            "providers.aws.services.directoryservice.directoryservice_service.DirectoryService",
            new=directoryservice_client,
        ):
            # Test Check
            from providers.aws.services.directoryservice.directoryservice_directory_monitor_notifications.directoryservice_directory_monitor_notifications import (
                directoryservice_directory_monitor_notifications,
            )

            check = directoryservice_directory_monitor_notifications()
            result = check.execute()

            assert len(result) == 1
            assert result[0].resource_id == "test-directory"
            assert result[0].region == AWS_REGION
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Directory Service {directory_name} have SNS messaging disabled"
            )

    def test_one_directory_logging_enabled(self):
        directoryservice_client = mock.MagicMock
        directory_name = "test-directory"
        directoryservice_client.directories = {
            directory_name: Directory(
                name=directory_name,
                region=AWS_REGION,
                event_topics=[
                    EventTopics(
                        topic_arn=f"arn:aws:sns:{AWS_REGION}:{DEFAULT_ACCOUNT_ID}:test-topic",
                        topic_name="test-topic",
                        status=EventTopicStatus.Registered,
                        created_date_time=datetime(2022, 1, 1),
                    )
                ],
            )
        }
        with mock.patch(
            "providers.aws.services.directoryservice.directoryservice_service.DirectoryService",
            new=directoryservice_client,
        ):
            # Test Check
            from providers.aws.services.directoryservice.directoryservice_directory_monitor_notifications.directoryservice_directory_monitor_notifications import (
                directoryservice_directory_monitor_notifications,
            )

            check = directoryservice_directory_monitor_notifications()
            result = check.execute()

            assert len(result) == 1
            assert result[0].resource_id == "test-directory"
            assert result[0].region == AWS_REGION
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Directory Service {directory_name} have SNS messaging enabled"
            )