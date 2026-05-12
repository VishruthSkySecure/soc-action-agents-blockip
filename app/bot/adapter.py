from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from app.core.config import settings
import traceback

adapter_settings = BotFrameworkAdapterSettings(
    app_id=settings.APP_ID,
    app_password=settings.APP_PASSWORD,
    channel_auth_tenant=settings.TENANT_ID,  # ← THIS is what's missing
)

adapter = BotFrameworkAdapter(adapter_settings)

async def on_error(context, error):
    print("=" * 60)
    print("BOT ERROR CAUGHT:")
    print(str(error))
    print(traceback.format_exc())
    print("=" * 60)
    # Don't try to send_activity here — if auth is broken this also fails
    # Just log it instead
    
adapter.on_turn_error = on_error