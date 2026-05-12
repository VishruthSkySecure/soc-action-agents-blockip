def get_ip_input_card() -> dict:
    """Card shown to user asking for IP input."""
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",          # 1.4 is the max Teams reliably supports
        "msteams": {"width": "Full"},  # fixes Teams narrow card width
        "body": [
            {
                "type": "TextBlock",
                "text": "🔒 Block IP Address",
                "weight": "Bolder",
                "size": "Large",
                "wrap": True       # always wrap=True in Teams
            },
            {
                "type": "TextBlock",
                "text": "Enter the IP address you want to block in Microsoft Defender.",
                "wrap": True,
                "isSubtle": True
            },
            {
                "type": "Input.Text",
                "id": "ip_address",
                "placeholder": "e.g. 203.0.113.10",
                "label": "IP Address",
                "isRequired": True,
                "regex": "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$",
                "errorMessage": "Please enter a valid IP address"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "🚫 Block IP",
                "data": {"action": "block_ip"}  # identifier for your handler
            }
        ]
    }


def get_result_card(ip: str, success: bool, detail: str = "") -> dict:
    """Card shown after block attempt."""
    color = "Good" if success else "Attention"
    icon  = "✅" if success else "❌"
    title = f"{icon} IP {'Blocked' if success else 'Block Failed'}"

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "msteams": {"width": "Full"},
        "body": [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "size": "Large",
                "color": color,
                "wrap": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "IP Address", "value": ip},
                    {"title": "Status",     "value": "Blocked in Defender" if success else "Failed"},
                    {"title": "Detail",     "value": detail or "N/A"},
                ]
            }
        ]
    }