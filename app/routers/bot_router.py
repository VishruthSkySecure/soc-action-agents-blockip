import json
from fastapi import APIRouter, Request, Response
from botbuilder.schema import Activity
from botbuilder.core import CardFactory, MessageFactory, TurnContext

from app.bot.adapter import adapter
from app.bot.bot import TeamsBot
from app.cards.approval_card import get_approval_card
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()
bot = TeamsBot()

# Store conversation reference when bot first gets a message
conversation_reference = None


@router.post("/api/messages")
async def messages(req: Request):
    global conversation_reference

    if "application/json" not in req.headers.get("Content-Type", ""):
        logger.warning("Received non-JSON request to /api/messages")
        return Response(status_code=415)

    body        = await req.json()
    activity    = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    logger.info(f"Received activity of type: {activity.type}")

    # Save conversation reference from message or conversationUpdate activities
    # (not from invoke — invoke doesn't have full conversation info)
    if activity.type in ("message", "conversationUpdate"):
        conversation_reference = TurnContext.get_conversation_reference(activity)
        logger.info(f"Saved conversation reference from {activity.type}.")

    invoke_response = await adapter.process_activity(
        activity,
        auth_header,
        bot.on_turn,
    )

    if invoke_response:
        logger.debug(f"Returning invoke response with status {invoke_response.status}")
        return Response(
            content=json.dumps(invoke_response.body),
            status_code=invoke_response.status,
            media_type="application/json",
        )

    # invoke activities need 200, everything else 201
    if activity.type == "invoke":
        return Response(status_code=200)

    return Response(status_code=201)


# ── TEST ENDPOINT — hit this to trigger the approval card ──────────
@router.get("/test/block")
async def test_block():
    global conversation_reference

    logger.info("Test block endpoint triggered.")

    if conversation_reference is None:
        logger.warning("Test block failed: No conversation reference yet.")
        return {"error": "No conversation yet. Message the bot in Teams first."}

    HARDCODED_IP     = "0.0.0.0"
    HARDCODED_REASON = "Suspicious port scan detected (test)"

    card       = get_approval_card(HARDCODED_IP, HARDCODED_REASON)
    attachment = CardFactory.adaptive_card(card)
    message    = MessageFactory.attachment(attachment)

    # ✅ Fixed: callback takes only turn_context (no second arg)
    async def send_card(turn_context: TurnContext):
        await turn_context.send_activity(message)

    await adapter.continue_conversation(
        conversation_reference,
        send_card,
        app_id=settings.APP_ID,
    )

    logger.info(f"Test approval card sent for IP: {HARDCODED_IP}")
    return {"status": "Approval card sent to Teams", "ip": HARDCODED_IP}