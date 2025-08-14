"""Slack integration module for sending reports to Slack channels."""

import json

# Type imports are handled in the mock classes if needed

try:
    import requests
except ImportError:
    print(
        "Warning: requests library not installed. Webhook functionality may not work."
    )

    class MockResponse:
        def __init__(self, status_code=200, text="OK"):
            self.status_code = status_code
            self.text = text

    class MockRequests:
        @staticmethod
        def post(*args, **kwargs):
            return MockResponse()

        class exceptions:
            RequestException = Exception

    requests = MockRequests()  # type: ignore

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    # Handle case where Slack SDK is not installed
    print("Warning: Slack SDK not installed. Slack features may not work.")

    class MockWebClient:
        def __init__(self, token: str):
            self.token = token

        def chat_postMessage(self, **kwargs):
            return {"ok": True}

        def auth_test(self):
            return {"user": "mock_bot"}

    class MockSlackApiError(Exception):
        def __init__(self, message: str):
            super().__init__(message)
            self.response = {"error": message}

    WebClient = MockWebClient  # type: ignore
    SlackApiError = MockSlackApiError  # type: ignore

from ..config import Config


class SlackSender:
    """Handles sending reports to Slack via webhook or bot token."""

    def __init__(self, config: Config):
        self.config = config
        self.webhook_url = config.slack_webhook_url
        self.client = None

        if config.slack_token:
            self.client = WebClient(token=config.slack_token)

    def send_report(
        self, report: str, title: str = "Git Repository Analysis Report"
    ) -> bool:
        """Send the report to Slack using the configured method."""

        # Try bot token method first (more reliable)
        if self.client:
            return self._send_via_bot_token(report, title)

        # Fallback to webhook method
        elif self.webhook_url:
            return self._send_via_webhook(report, title)

        else:
            print(
                "Error: No Slack configuration found. Please set SLACK_TOKEN or SLACK_WEBHOOK_URL."
            )
            return False

    def _send_via_bot_token(self, report: str, title: str) -> bool:
        """Send report using Slack bot token."""
        try:
            # Split long reports into multiple messages if needed
            max_length = 4000  # Slack message limit

            if len(report) <= max_length:
                # Send as single message
                if self.client is not None:
                    self.client.chat_postMessage(
                        channel=self.config.slack_channel,
                        text=f"*{title}*\n\n{report}",
                        mrkdwn=True,
                    )
                print(f"Report sent successfully to {self.config.slack_channel}")
                return True

            else:
                # Split into multiple messages
                return self._send_long_report_via_bot(report, title)

        except SlackApiError as e:
            print(f"Error sending to Slack: {e.response['error']}")
            return False
        except Exception as e:
            print(f"Unexpected error sending to Slack: {e}")
            return False

    def _send_long_report_via_bot(self, report: str, title: str) -> bool:
        """Send a long report by splitting it into multiple messages."""
        try:
            if self.client is None:
                return False

            # Send title first
            self.client.chat_postMessage(
                channel=self.config.slack_channel, text=f"*{title}*", mrkdwn=True
            )

            # Split report by sections (looking for ## headers)
            sections = self._split_report_by_sections(report)

            for section in sections:
                if section.strip():
                    self.client.chat_postMessage(
                        channel=self.config.slack_channel, text=section, mrkdwn=True
                    )

            print(
                f"Long report sent successfully in {len(sections)} parts to {self.config.slack_channel}"
            )
            return True

        except SlackApiError as e:
            print(f"Error sending long report to Slack: {e.response['error']}")
            return False

    def _send_via_webhook(self, report: str, title: str) -> bool:
        """Send report using Slack webhook."""
        try:
            # Prepare the payload
            payload = {
                "text": f"*{title}*\n\n{report}",
                "mrkdwn": True,
                "channel": self.config.slack_channel,
            }

            # Send to webhook
            if not self.webhook_url:
                raise ValueError("Webhook URL is not configured")

            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                print(
                    f"Report sent successfully via webhook to {self.config.slack_channel}"
                )
                return True
            else:
                print(
                    f"Webhook request failed with status {response.status_code}: {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error sending webhook to Slack: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending webhook to Slack: {e}")
            return False

    def _split_report_by_sections(
        self, report: str, max_length: int = 4000
    ) -> list[str]:
        """Split a report into sections based on markdown headers."""
        sections = []
        current_section = ""

        lines = report.split("\n")

        for line in lines:
            # Check if this line would make the current section too long
            if len(current_section) + len(line) + 1 > max_length:
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = line
            else:
                if current_section:
                    current_section += "\n" + line
                else:
                    current_section = line

            # If we hit a section header and have content, consider breaking
            if line.startswith("##") and current_section.strip():
                if len(current_section) > max_length * 0.7:  # 70% of max length
                    sections.append(current_section.strip())
                    current_section = ""

        # Add the last section
        if current_section.strip():
            sections.append(current_section.strip())

        return sections

    def test_connection(self) -> bool:
        """Test the Slack connection."""
        if self.client:
            try:
                response = self.client.auth_test()
                print(f"Slack bot connection successful. Bot user: {response['user']}")
                return True
            except SlackApiError as e:
                print(f"Slack bot connection failed: {e.response['error']}")
                return False

        elif self.webhook_url:
            try:
                # Send a simple test message
                payload = {
                    "text": "🔍 Git Sniff Otter connection test successful!",
                    "channel": self.config.slack_channel,
                }

                response = requests.post(
                    self.webhook_url,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )

                if response.status_code == 200:
                    print("Slack webhook connection successful")
                    return True
                else:
                    print(
                        f"Slack webhook test failed with status {response.status_code}"
                    )
                    return False

            except requests.exceptions.RequestException as e:
                print(f"Slack webhook connection failed: {e}")
                return False

        else:
            print("No Slack configuration found")
            return False
