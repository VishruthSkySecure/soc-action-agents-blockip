def get_result_card(ip: str, success: bool, detail: str = "", rejected: bool = False) -> dict:
    if rejected:
        color, icon, title = "Warning", "🚫", "Block Rejected by Admin"
        status = "No action taken"
    elif success:
        color, icon, title = "Good",    "✅", "IP Blocked Successfully"
        status = "Active in Microsoft Defender"
    else:
        color, icon, title = "Attention","❌", "Block Failed"
        status = "See detail for reason"

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "msteams": {"width": "Full"},
        "body": [
            {
                "type": "TextBlock",
                "text": f"{icon} {title}",
                "weight": "Bolder",
                "size": "Large",
                "color": color,
                "wrap": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "IP Address", "value": ip},
                    {"title": "Status",     "value": status},
                    {"title": "Detail",     "value": detail or "—"},
                ]
            }
        ]
    }