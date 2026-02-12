"""
Tests for the tool executor.

Tests tool routing and execution for different agent types.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.agents.executors.tool_executor import ToolExecutor
from app.agents.registry import AgentType


class TestToolExecutorRouting:
    """Tests for tool routing logic."""

    def test_executor_initializes_with_agent_type(self):
        """ToolExecutor initializes with agent type and tools."""
        executor = ToolExecutor(AgentType.BOOKKEEPER, {})
        assert executor.agent_type == AgentType.BOOKKEEPER

    def test_executor_stores_tools(self):
        """ToolExecutor stores provided tools."""
        mock_tools = {"quickbooks": MagicMock()}
        executor = ToolExecutor(AgentType.BOOKKEEPER, mock_tools)
        assert executor.tools == mock_tools

    @pytest.mark.asyncio
    async def test_unknown_agent_returns_error(self):
        """Unknown agent type returns error."""
        # Create executor with a valid type but then test the fallback
        executor = ToolExecutor(AgentType.BOOKKEEPER, {})
        # Override agent type to something invalid
        executor.agent_type = "invalid_type"

        result = await executor.execute("some_tool", {})
        assert "error" in result


class TestBookkeeperToolExecution:
    """Tests for bookkeeper agent tool execution."""

    @pytest.mark.asyncio
    async def test_get_transactions_routes_correctly(self):
        """get_transactions tool routes to QuickBooks tools."""
        mock_qb_tools = MagicMock()
        mock_qb_tools.get_transactions = AsyncMock(return_value={"transactions": []})

        executor = ToolExecutor(
            AgentType.BOOKKEEPER,
            {"quickbooks": mock_qb_tools}
        )

        result = await executor.execute(
            "get_transactions",
            {"start_date": "2026-01-01", "end_date": "2026-01-31"}
        )

        mock_qb_tools.get_transactions.assert_called_once_with(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        """Unknown tool name returns error."""
        mock_qb_tools = MagicMock()
        executor = ToolExecutor(
            AgentType.BOOKKEEPER,
            {"quickbooks": mock_qb_tools}
        )

        result = await executor.execute("nonexistent_tool", {})
        assert "error" in result
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_missing_tools_returns_error(self):
        """Missing tools configuration returns error."""
        executor = ToolExecutor(AgentType.BOOKKEEPER, {})

        result = await executor.execute("get_transactions", {})
        assert "error" in result


class TestInboxCommanderToolExecution:
    """Tests for inbox commander agent tool execution."""

    @pytest.mark.asyncio
    async def test_get_emails_routes_correctly(self):
        """get_emails tool routes to Gmail tools."""
        mock_gmail = MagicMock()
        mock_gmail.get_emails = AsyncMock(return_value={"emails": []})

        executor = ToolExecutor(
            AgentType.INBOX_COMMANDER,
            {"gmail": mock_gmail}
        )

        result = await executor.execute("get_emails", {"limit": 10})

        mock_gmail.get_emails.assert_called_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_send_email_routes_correctly(self):
        """send_email tool routes to Gmail tools."""
        mock_gmail = MagicMock()
        mock_gmail.send_email = AsyncMock(return_value={"sent": True})

        executor = ToolExecutor(
            AgentType.INBOX_COMMANDER,
            {"gmail": mock_gmail}
        )

        result = await executor.execute(
            "send_email",
            {"to": "test@test.com", "subject": "Hi", "body": "Hello"}
        )

        mock_gmail.send_email.assert_called_once()


class TestAppointmentToolExecution:
    """Tests for appointment setter agent tool execution."""

    @pytest.mark.asyncio
    async def test_book_appointment_routes_correctly(self):
        """book_appointment tool routes to Calendar tools."""
        mock_calendar = MagicMock()
        mock_calendar.book_appointment = AsyncMock(return_value={"event_id": "123"})

        executor = ToolExecutor(
            AgentType.APPOINTMENT,
            {"calendar": mock_calendar}
        )

        result = await executor.execute(
            "book_appointment",
            {"title": "Meeting", "start": "2026-01-15T10:00:00"}
        )

        mock_calendar.book_appointment.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_available_slots_routes_correctly(self):
        """find_available_slots tool routes to Calendar tools."""
        mock_calendar = MagicMock()
        mock_calendar.find_available_slots = AsyncMock(return_value={"slots": []})

        executor = ToolExecutor(
            AgentType.APPOINTMENT,
            {"calendar": mock_calendar}
        )

        result = await executor.execute(
            "find_available_slots",
            {"date": "2026-01-15", "duration_minutes": 30}
        )

        mock_calendar.find_available_slots.assert_called_once()
