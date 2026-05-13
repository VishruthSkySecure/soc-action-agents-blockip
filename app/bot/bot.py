from botbuilder.core import TurnContext, CardFactory, MessageFactory
from botbuilder.schema import ActivityTypes, Activity

from app.cards.approval_card import get_approval_card
from app.cards.result_card import get_result_card
from app.services.defender import block_ip
from app.core.logger import logger


class TeamsBot:
    def __init__(self):
        # Keep track of processed request IDs to prevent duplicate actions
        self.processed_requests = set()

    async def on_turn(self, turn_context: TurnContext):
        activity = turn_context.activity

        if activity.type == ActivityTypes.message:
            logger.info("Received message activity.")
            await self._handle_message(turn_context)

        elif activity.type == "invoke":
            logger.info("Received invoke activity.")
            await self._handle_invoke(turn_context)

        else:
            logger.info(f"Unhandled activity type: {activity.type}")

    # ── Incoming text messages ─────────────────────────────────────
    async def _handle_message(self, turn_context: TurnContext):
        # Handle Action.Submit from Adaptive Cards that arrive as messages
        value = turn_context.activity.value
        if value and isinstance(value, dict) and "action" in value:
            logger.info("Intercepted Action.Submit value from message.")
            return await self._handle_invoke(turn_context)

        text = (turn_context.activity.text or "").strip().lower()
        logger.debug(f"Message text: {text}")

        if "help" in text or not text:
            logger.info("Sending help message.")
            await turn_context.send_activity(
                "👋 I monitor for suspicious IPs.\n\n"
                "When one is detected I'll send an approval card here.\n"
                "You can also type: **block ip <address>** to manually trigger a review."
            )
            return

        # Manual trigger: "block" or "block ip 1.2.3.4"
        if text.startswith("block"):
            parts = text.split()
            # If user just types "block" or "block ip", use a hardcoded IP for testing
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == "ip"):
                ip = "0.0.0.0"  # Hardcoded testing IP
                logger.info(f"Manual trigger invoked with default hardcoded IP: {ip}")
            else:
                ip = parts[-1]  # The last part is assumed to be the IP
                
            logger.info(f"Manual trigger for IP: {ip}")
            await self._send_approval_card(turn_context, ip, "Manually triggered via chat command")
            return

        logger.info("Sending fallback message.")
        await turn_context.send_activity("Type **help** to see what I can do.")

    # ── Adaptive Card button clicks arrive here ────────────────────
    async def _handle_invoke(self, turn_context: TurnContext):
        value  = turn_context.activity.value or {}
        
        # If it's a Teams invoke, the actual data might be nested under 'value'
        if "action" not in value and "value" in value and isinstance(value["value"], dict):
            value = value["value"]
            
        action          = value.get("action")
        ip              = value.get("ip_address", "").strip()
        request_id      = value.get("request_id")
        original_reason = value.get("original_reason", "Suspicious activity detected")
        admin_reason    = value.get("admin_reason", "").strip()
        
        logger.info(f"Invoke action: {action} for IP: {ip}, Request ID: {request_id}, Reason: {admin_reason}")

        # Check if we already processed this specific card
        if request_id:
            if request_id in self.processed_requests:
                logger.info(f"Duplicate request detected for {request_id}. Ignoring.")
                await turn_context.send_activity("⚠️ This request has already been processed.")
                
                # Still need to return the invokeResponse if it was an invoke
                if turn_context.activity.type == ActivityTypes.invoke:
                    invoke_response = Activity(type="invokeResponse", value={"status": 200})
                    await turn_context.send_activity(invoke_response)
                return
            
            # Mark as processed
            self.processed_requests.add(request_id)

        if action == "approve_block":
            await self._do_block(turn_context, ip, admin_reason, original_reason, request_id)

        elif action == "reject_block":
            await self._do_reject(turn_context, ip, admin_reason, original_reason, request_id)

        # ✅ REQUIRED: Tell Teams the invoke was handled successfully
        if turn_context.activity.type == ActivityTypes.invoke:
            invoke_response = Activity(
                type="invokeResponse",
                value={"status": 200}
            )
            await turn_context.send_activity(invoke_response)

    # ── Send the approval card to Teams ───────────────────────────
    async def _send_approval_card(
        self,
        turn_context: TurnContext,
        ip: str,
        reason: str = "Suspicious activity detected"
    ):
        logger.info(f"Sending approval card for IP: {ip}, Reason: {reason}")
        card       = get_approval_card(ip, reason)
        attachment = CardFactory.adaptive_card(card)
        await turn_context.send_activity(MessageFactory.attachment(attachment))

    # ── Admin clicked Accept ───────────────────────────────────────
    async def _do_block(self, turn_context: TurnContext, ip: str, admin_reason: str = "", original_reason: str = "", request_id: str = ""):
        logger.info(f"Executing block for IP: {ip}. Admin Reason: {admin_reason}")
        
        # 1. Update the ORIGINAL card to remove buttons
        try:
            # Reconstruct the original card but remove the actions
            orig_card = get_approval_card(ip, original_reason, request_id)
            orig_card["actions"] = [] # Remove buttons
            
            # Update status in the original card facts
            for item in orig_card["body"]:
                if item["type"] == "FactSet":
                    for fact in item["facts"]:
                        if fact["title"] == "Status":
                            fact["value"] = "✅ Processed (Blocked)"
            
            update_activity = MessageFactory.attachment(CardFactory.adaptive_card(orig_card))
            update_activity.id = turn_context.activity.reply_to_id
            await turn_context.update_activity(update_activity)
        except Exception as e:
            logger.error(f"Failed to update original card: {e}")

        # 2. Proceed with the actual blocking
        await turn_context.send_activity(f"⏳ Blocking `{ip}` in Microsoft Defender...")
        result = block_ip(ip)

        detail = ""
        if result["success"]:
            detail = str(result.get("data", {}).get("id", "Indicator created"))
            logger.info(f"Successfully blocked IP: {ip}. Detail: {detail}")
            print(f"\n[SUCCESS] Blocked IP: {ip}\n[SUCCESS] Admin Reason: {admin_reason}\n[SUCCESS] Response ID: {detail}\n")
        else:
            detail = str(result.get("error", "Unknown error"))
            logger.error(f"Failed to block IP: {ip}. Error: {detail}")
            print(f"\n[FAILED] Could not block IP: {ip}\n[FAILED] Error Details: {detail}\n")

        # 3. Send the RESULT card as a NEW message
        card       = get_result_card(ip, result["success"], detail, admin_reason=admin_reason)
        attachment = CardFactory.adaptive_card(card)
        await turn_context.send_activity(MessageFactory.attachment(attachment))

    # ── Admin clicked Reject ───────────────────────────────────────
    async def _do_reject(self, turn_context: TurnContext, ip: str, admin_reason: str = "", original_reason: str = "", request_id: str = ""):
        logger.info(f"Rejecting block for IP: {ip}. Admin Reason: {admin_reason}")
        
        # 1. Update the ORIGINAL card to remove buttons
        try:
            orig_card = get_approval_card(ip, original_reason, request_id)
            orig_card["actions"] = [] # Remove buttons
            
            for item in orig_card["body"]:
                if item["type"] == "FactSet":
                    for fact in item["facts"]:
                        if fact["title"] == "Status":
                            fact["value"] = "🚫 Processed (Rejected)"
            
            update_activity = MessageFactory.attachment(CardFactory.adaptive_card(orig_card))
            update_activity.id = turn_context.activity.reply_to_id
            await turn_context.update_activity(update_activity)
        except Exception as e:
            logger.error(f"Failed to update original card: {e}")

        # 2. Send the RESULT card as a NEW message
        detail = "Admin chose not to block this IP"
        card   = get_result_card(ip, success=False, rejected=True, detail=detail, admin_reason=admin_reason)
        attachment = CardFactory.adaptive_card(card)
        await turn_context.send_activity(MessageFactory.attachment(attachment))