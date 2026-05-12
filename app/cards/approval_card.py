def get_approval_card(ip: str, reason: str = "Suspicious activity detected") -> dict:
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "msteams": {"width": "Full"},
        "body": [
            {
                "type": "TextBlock",
                "text": "⚠️ IP Block Approval Required",
                "weight": "Bolder",
                "size": "Large",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": "A suspicious IP has been flagged. Admin action required.",
                "wrap": True,
                "isSubtle": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "IP Address", "value": ip},
                    {"title": "Reason",     "value": reason},
                    {"title": "Status",     "value": "⏳ Awaiting approval"},
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "✅ Accept — Block IP",
                "style": "positive",          # green button in Teams
                "data": {
                    "action":     "approve_block",
                    "ip_address": ip           # carry IP through to handler
                }
            },
            {
                "type": "Action.Submit",
                "title": "❌ Reject — Do Nothing",
                "style": "destructive",        # red button in Teams
                "data": {
                    "action":     "reject_block",
                    "ip_address": ip
                }
            }
        ]
    }