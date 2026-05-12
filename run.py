from app.core.config import settings

print("=" * 60)
print(f"APP_ID:      '{settings.APP_ID}'")
print(f"APP_PASSWORD: '{settings.APP_PASSWORD[:4]}...{settings.APP_PASSWORD[-4:]}'")
print(f"TENANT_ID:   '{settings.TENANT_ID}'")
print(f"APP_ID empty?      {not settings.APP_ID}")
print(f"PASSWORD empty?    {not settings.APP_PASSWORD}")
print("=" * 60)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3978, reload=False)