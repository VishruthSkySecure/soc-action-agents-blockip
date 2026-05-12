import requests
from app.core.config import settings
from app.core.logger import logger

def get_token() -> str | None:
    logger.info("Requesting Microsoft Defender API token...")
    url = f"https://login.microsoftonline.com/{settings.DEFENDER_TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "client_id":     settings.DEFENDER_CLIENT_ID,
        "client_secret": settings.DEFENDER_CLIENT_SECRET,
        "scope":         "https://api.securitycenter.microsoft.com/.default",
        "grant_type":    "client_credentials",
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            logger.info("Successfully acquired Defender API token.")
            return r.json()["access_token"]
        
        logger.error(f"Failed to acquire token. Status code: {r.status_code}, Response: {r.text}")
    except Exception as e:
        logger.exception("Exception occurred while requesting Defender token")
    return None

def block_ip(ip_address: str) -> dict:
    """Block an IP via Defender. Returns result dict."""
    logger.info(f"Initiating block for IP: {ip_address}")
    token = get_token()
    if not token:
        logger.error(f"Cannot block IP {ip_address}: Failed to obtain token.")
        return {"success": False, "error": "Could not obtain token"}

    url = "https://api.security.microsoft.com/api/indicators"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    payload = {
        "indicatorValue": ip_address,
        "indicatorType":  "IpAddress",
        "action":         "Block",
        "title":          f"Blocked via Teams Bot",
        "description":    f"IP {ip_address} blocked via Teams automation",
        "severity":       "High",
    }
    
    logger.debug(f"Sending block request to Defender for IP: {ip_address}")
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code in (200, 201):
            logger.info(f"Successfully blocked IP: {ip_address} in Defender.")
            return {"success": True, "data": r.json()}
        
        logger.error(f"Failed to block IP {ip_address}. Status code: {r.status_code}, Response: {r.text}")
        return {"success": False, "error": r.json()}
    except Exception as e:
        logger.exception(f"Exception occurred while blocking IP: {ip_address}")
        return {"success": False, "error": str(e)}