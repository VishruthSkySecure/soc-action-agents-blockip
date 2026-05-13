import uuid

def get_approval_card(ip: str, reason: str = "Suspicious activity detected", request_id: str = None) -> dict:
    if not request_id:
        request_id = str(uuid.uuid4())
        
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
                "type": "Action.ShowCard",
                "title": "✅ Accept — Block IP",
                "style": "positive",          # green button in Teams
                "card": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "Input.Text",
                            "id": "admin_reason",
                            "placeholder": "Mention the reason for accepting to block this IP",
                            "isMultiline": True,
                            "maxLength": 500
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Confirm Accept",
                            "data": {
                                "action":          "approve_block",
                                "ip_address":      ip,          
                                "request_id":      request_id,
                                "original_reason": reason
                            }
                        }
                    ]
                }
            },
            {
                "type": "Action.ShowCard",
                "title": "❌ Reject — Do Nothing",
                "style": "destructive",        # red button in Teams
                "card": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "Input.Text",
                            "id": "admin_reason",
                            "placeholder": "Mention the reason for rejecting this block",
                            "isMultiline": True,
                            "maxLength": 500
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Confirm Reject",
                            "data": {
                                "action":          "reject_block",
                                "ip_address":      ip,
                                "request_id":      request_id,
                                "original_reason": reason
                            }
                        }
                    ]
                }
            }
        ]
    }