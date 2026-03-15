import logging
from datetime import datetime

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response

import mcp.types as types
from mcp.server import Server
from mcp.server.sse import SseServerTransport

from app.database import async_session
from sqlalchemy import select
from app.reservations.models import Reservation, Table

logger = logging.getLogger(__name__)

# Initialize the MCP Server Instance
mcp_server = Server("gestronomy-voicebooker-mcp")

# SseServerTransport takes the *relative* URL path that handles POST messages.
# The Starlette sub-app is mounted at /mcp/voicebooker in main.py,
# so the POST endpoint is at /mcp/voicebooker/messages.
sse = SseServerTransport("/mcp/voicebooker/messages")


# --- AI Tool Implementations ---

async def check_table_availability(date: str, time: str, party_size: int) -> str:
    """Checks if the restaurant has an available table for a specific date, time, and party size."""
    async with async_session() as session:
        try:
            req_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return "Error: Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time."

        tables_res = await session.execute(
            select(Table).where(Table.capacity >= party_size, Table.is_active.is_(True))
        )
        available_tables = tables_res.scalars().all()

        if not available_tables:
            return f"Unfortunately, we do not have tables that can accommodate a party of {party_size}."

        conflicts_res = await session.execute(
            select(Reservation).where(
                Reservation.reservation_date == req_datetime.date(),
                Reservation.status.in_(["confirmed", "seated", "arrived"]),
            )
        )
        existing_res = conflicts_res.scalars().all()

        if len(existing_res) >= len(available_tables):
            return f"I'm sorry, we are fully booked on {date} around {time}. No tables available."

        return f"Yes! We currently have availability on {date} at {time} for {party_size} guests."


async def create_reservation(
    name: str, phone: str, date: str, time: str, party_size: int, notes: str = ""
) -> str:
    """Officially creates a confirmed reservation in the database."""
    async with async_session() as session:
        try:
            req_date = datetime.strptime(date, "%Y-%m-%d").date()
            req_time = datetime.strptime(time, "%H:%M").time()
        except ValueError:
            return "Error: Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time."

        new_res = Reservation(
            restaurant_id=1,  # Default tenant — VoiceBooker doesn't carry tenant context
            guest_name=name,
            guest_phone=phone,
            reservation_date=req_date,
            start_time=req_time,
            party_size=party_size,
            notes=notes,
            status="confirmed",
            source="voicebooker_mcp",
        )

        session.add(new_res)
        await session.commit()
        await session.refresh(new_res)

        return f"Reservation successfully confirmed for {name} on {date} at {time} (ID: {new_res.id})."


async def cancel_reservation(reservation_id: int) -> str:
    """Cancels an existing reservation by its ID."""
    async with async_session() as session:
        result = await session.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        res = result.scalar_one_or_none()

        if not res:
            return f"Error: Reservation with ID {reservation_id} not found."

        res.status = "cancelled"
        await session.commit()

        return f"Reservation {reservation_id} for {res.guest_name} has been successfully cancelled."


# --- MCP Tool Registrations ---


@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="check_table_availability",
            description="Checks if the restaurant has an available table for a specific date (YYYY-MM-DD), time (HH:MM), and party size.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM format (24 hour)"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                },
                "required": ["date", "time", "party_size"],
            },
        ),
        types.Tool(
            name="create_reservation",
            description="Officially creates a confirmed reservation in the database. Call this ONLY after explicitly confirming the details with the user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer Full Name"},
                    "phone": {"type": "string", "description": "Customer Phone Number"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM format (24 hour)"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "notes": {"type": "string", "description": "Any special requests or allergies"},
                },
                "required": ["name", "phone", "date", "time", "party_size"],
            },
        ),
        types.Tool(
            name="cancel_reservation",
            description="Cancels an existing reservation in the system using its unique ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "reservation_id": {
                        "type": "integer",
                        "description": "The unique ID of the reservation to cancel",
                    }
                },
                "required": ["reservation_id"],
            },
        ),
    ]


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    args = arguments or {}
    try:
        if name == "check_table_availability":
            result = await check_table_availability(**args)
        elif name == "create_reservation":
            result = await create_reservation(**args)
        elif name == "cancel_reservation":
            result = await cancel_reservation(**args)
        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]

        return [types.TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Error executing Tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error executing tool: {str(e)}")]


# --- ASGI Transport Endpoints ---
# These use raw Starlette handlers to pass the real ASGI scope/receive/send
# to the MCP SSE transport — FastAPI's Request object doesn't expose the raw send callable.


async def handle_sse(request: Request) -> Response:
    """SSE connection point for VoiceBooker's MCP Client."""
    logger.info("MCP SSE connection initiated from %s", request.client)
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )
    return Response()


async def handle_messages(request: Request) -> Response:
    """Endpoint where the VoiceBooker MCP Client sends JSON-RPC messages."""
    logger.info("MCP message received from %s", request.client)
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response()


# Starlette sub-application — mounted in main.py via `app.mount("/mcp/voicebooker", mcp_app)`
mcp_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ],
)
