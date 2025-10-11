from fastapi import APIRouter, Request, HTTPException, Response, Depends
from fastapi.responses import RedirectResponse, JSONResponse
import shopify
import os
import hmac
import hashlib
import binascii
from urllib.parse import urlencode
import logging
from typing import Dict
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/shopify", tags=["auth"])

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY", "")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET", "")
SHOPIFY_SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,write_products,read_orders").split(",")
SHOPIFY_REDIRECT_URI = os.getenv("SHOPIFY_REDIRECT_URI", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-10")

if not SHOPIFY_API_KEY or not SHOPIFY_API_SECRET:
    logger.warning("SHOPIFY_API_KEY and SHOPIFY_API_SECRET must be set for OAuth to work")

if SHOPIFY_API_KEY and SHOPIFY_API_SECRET:
    shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)

# In-memory session store (IMPORTANT: Use Redis or database in production)
oauth_states: Dict[str, str] = {}
shop_sessions: Dict[str, str] = {}


@router.get("/install")
async def install_app(shop: str = None):
    """
    Initiate Shopify OAuth flow
    """
    if not shop:
        raise HTTPException(status_code=400, detail="Shop parameter is required")
    
    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"
    
    if not SHOPIFY_API_KEY or not SHOPIFY_API_SECRET:
        raise HTTPException(
            status_code=500, 
            detail="Shopify API credentials not configured. Please set SHOPIFY_API_KEY and SHOPIFY_API_SECRET environment variables."
        )
    
    # Generate cryptographically secure state token
    state = secrets.token_urlsafe(32)
    oauth_states[state] = shop
    
    redirect_uri = SHOPIFY_REDIRECT_URI or f"{os.getenv('PUBLIC_URL', '')}/api/auth/shopify/callback"
    
    try:
        shopify_session = shopify.Session(shop, SHOPIFY_API_VERSION)
        auth_url = shopify_session.create_permission_url(
            redirect_uri,
            SHOPIFY_SCOPES,
            state
        )
        
        logger.info(f"Redirecting to Shopify OAuth: {shop}")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating OAuth: {str(e)}")


@router.get("/callback")
async def oauth_callback(request: Request):
    """
    Handle Shopify OAuth callback
    """
    params = dict(request.query_params)
    
    shop = params.get("shop")
    code = params.get("code")
    state = params.get("state")
    
    if not shop or not code or not state:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    # Validate state to prevent CSRF attacks
    if state not in oauth_states or oauth_states[state] != shop:
        raise HTTPException(status_code=401, detail="Invalid state parameter - possible CSRF attack")
    
    # Remove used state token
    del oauth_states[state]
    
    # Verify HMAC signature (MUST have secret configured)
    if not verify_shopify_hmac(params):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
    
    try:
        shopify_session = shopify.Session(shop, SHOPIFY_API_VERSION)
        access_token = shopify_session.request_token(params)
        
        # Store access token server-side (NOT in cookies)
        session_id = secrets.token_urlsafe(32)
        shop_sessions[session_id] = {
            "shop": shop,
            "access_token": access_token
        }
        
        logger.info(f"OAuth successful for shop: {shop}")
        
        # Set secure, httponly session cookie
        response = RedirectResponse(url=f"/?shop={shop}&installed=true")
        response.set_cookie(
            key="shopify_session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400 * 30  # 30 days
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error completing OAuth: {str(e)}")


@router.get("/verify")
async def verify_session(request: Request):
    """
    Verify if the current session is authenticated with Shopify
    """
    session_id = request.cookies.get("shopify_session_id")
    
    if not session_id or session_id not in shop_sessions:
        return JSONResponse(
            status_code=401,
            content={"authenticated": False, "message": "No session found"}
        )
    
    try:
        session_data = shop_sessions[session_id]
        shop = session_data["shop"]
        token = session_data["access_token"]
        
        with shopify.Session.temp(shop, SHOPIFY_API_VERSION, token):
            shop_info = shopify.Shop.current()
            
            return JSONResponse(content={
                "authenticated": True,
                "shop": shop,
                "shop_name": shop_info.name,
                "shop_email": shop_info.email
            })
    
    except Exception as e:
        logger.error(f"Session verification failed: {str(e)}")
        # Cleanup invalid session
        if session_id in shop_sessions:
            del shop_sessions[session_id]
        return JSONResponse(
            status_code=401,
            content={"authenticated": False, "message": "Invalid session"}
        )


@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Clear Shopify session
    """
    session_id = request.cookies.get("shopify_session_id")
    
    # Remove session from server-side store
    if session_id and session_id in shop_sessions:
        del shop_sessions[session_id]
    
    # Delete session cookie
    response.delete_cookie("shopify_session_id")
    return {"message": "Logged out successfully"}


def verify_shopify_hmac(params: dict) -> bool:
    """
    Verify Shopify HMAC signature
    """
    # SECURITY: Always require SHOPIFY_API_SECRET for HMAC verification
    if not SHOPIFY_API_SECRET:
        logger.error("SHOPIFY_API_SECRET not set - cannot verify HMAC signature")
        return False
    
    hmac_value = params.get("hmac")
    if not hmac_value:
        logger.error("No HMAC value in request parameters")
        return False
    
    params_copy = params.copy()
    params_copy.pop("hmac", None)
    params_copy.pop("signature", None)
    
    message = "&".join([f"{k}={v}" for k, v in sorted(params_copy.items())])
    
    computed_hmac = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    is_valid = hmac.compare_digest(computed_hmac, hmac_value)
    
    if not is_valid:
        logger.warning(f"HMAC verification failed for params: {params_copy}")
    
    return is_valid
