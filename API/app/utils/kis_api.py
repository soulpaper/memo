import httpx
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Simple in-memory cache for tokens: {(app_key, app_secret): {"token": str, "expired": datetime}}
# In production, this should be in Redis or DB.
TOKEN_CACHE = {}

class KisApi:
    def __init__(self, app_key: str, app_secret: str, account_no: str, account_prod: str = "01", is_virtual: bool = False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.account_no = account_no
        self.account_prod = account_prod
        self.is_virtual = is_virtual
        
        self.base_url = "https://openapivts.koreainvestment.com:29443" if is_virtual else "https://openapi.koreainvestment.com:9443"
        self.token: Optional[str] = None
        self.token_expired: Optional[datetime] = None 

    async def get_access_token(self) -> str:
        """
        Gets access token using caching strategy.
        """
        cache_key = (self.app_key, self.app_secret)
        cached = TOKEN_CACHE.get(cache_key)
        
        if cached:
            # Check expiration (buffer 5 mins)
            if cached["expired"] > datetime.now() + timedelta(minutes=5):
                self.token = cached["token"]
                return self.token
        
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)
            if response.status_code != 200:
                logger.error(f"Failed to get token: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            self.token = data["access_token"]
            
            # expiration format: "2022-08-30 13:22:22"
            expired_str = data["access_token_token_expired"]
            self.token_expired = datetime.strptime(expired_str, "%Y-%m-%d %H:%M:%S")
            
            # Update cache
            TOKEN_CACHE[cache_key] = {
                "token": self.token,
                "expired": self.token_expired
            }
            
            return self.token

    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Fetches the account balance (holdings).
        """
        if not self.token:
            await self.get_access_token()
            
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        
        tr_id = "VTTC8434R" if self.is_virtual else "TTTC8434R"
        
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id
        }
        
        params = {
            "CANO": self.account_no,        # Account Number (8)
            "ACNT_PRDT_CD": self.account_prod, # Account Product Code (2)
            "AFHR_FLPR_YN": "N",            # After-hours price (N: No)
            "OFL_YN": "N",                  # Offline (N: No)
            "INQR_DVSN": "02",              # Inquiry Division (02: By Stock)
            "UNPR_DVSN": "01",              # Unit Price Division (01: Average)
            "FUND_STTL_ICLD_YN": "N",       # Fund Settlement Included (N: No)
            "FNCG_AMT_AUTO_RDPT_YN": "N",   # Financing Amount Auto Repayment (N: No)
            "PRCS_DVSN": "00",              # Process Division (00: All)
            "CTX_AREA_FK100": "",           # Context Area Key (Blank for first page)
            "CTX_AREA_NK100": ""            # Context Area Key (Blank for first page)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            # Log error if any
            if response.status_code != 200:
                logger.error(f"Balance fetch error: {response.text}")
            response.raise_for_status()
            return response.json()

    async def get_current_price(self, stock_code: str):
        """
        Get current price for a single stock.
        """
        if not self.token:
            await self.get_access_token()
            
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"
        }
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J", # Market Division Code (J: Stock)
            "FID_INPUT_ISCD": stock_code   # Input Item Code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                logger.error(f"Price fetch error: {response.text}")
            response.raise_for_status()
            data = response.json()
            return data.get("output", {}).get("stck_prpr")
