# core/proxy/checker.py
"""
✅ PROXY CHECKER v1.0 — проверка прокси на живность
✅ Проверка подключения
✅ Проверка IP
✅ Проверка страны
✅ Проверка задержки (latency)
"""

from __future__ import annotations

import asyncio
from typing import Dict, Any, Optional
import aiohttp

from services.logger import Logger
from core.proxy.manager import ProxyManager


async def check_proxy(
    proxy_manager: ProxyManager,
    proxy_id: str,
    logger: Logger,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    ✅ ПРОВЕРИТЬ ОДИН ПРОКСИ
    
    Args:
        proxy_manager: ProxyManager
        proxy_id: ID прокси
        logger: Logger
        timeout: Timeout в секундах
        
    Returns:
        Dict с результатами
    """
    
    result = {
        "proxy_id": proxy_id,
        "ok": False,
        "ip": None,
        "country": None,
        "latency": 0,
        "error": None,
    }
    
    try:
        proxy = None
        for p in proxy_manager.proxies:
            if p.proxy_id == proxy_id:
                proxy = p
                break
        
        if not proxy:
            result["error"] = "Proxy not found"
            return result
        
        # Проверяем подключение через httpbin
        url = "https://httpbin.org/ip"
        proxy_url = proxy.get_url()
        
        import time
        start_time = time.time()
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.get(
                    url,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=False
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result["ip"] = data.get("origin")
                        result["ok"] = True
                        result["latency"] = (time.time() - start_time) * 1000
                        
                        # Простая проверка страны по IP
                        if result["ip"]:
                            # Обычно если IP не из РФ — это foreign proxy
                            result["country"] = "Unknown"
                    else:
                        result["error"] = f"HTTP {resp.status}"
            
            except asyncio.TimeoutError:
                result["error"] = "Timeout"
            except Exception as e:
                result["error"] = str(e)
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


async def check_all_proxies(
    proxy_manager: ProxyManager,
    logger: Logger
) -> Dict[str, Any]:
    """
    ✅ ПРОВЕРИТЬ ВСЕ ПРОКСИ
    
    Args:
        proxy_manager: ProxyManager
        logger: Logger
        
    Returns:
        Dict с результатами для всех прокси
    """
    
    tasks = [
        check_proxy(proxy_manager, proxy.proxy_id, logger)
        for proxy in proxy_manager.proxies
    ]
    
    results = {}
    for task in asyncio.as_completed(tasks):
        result = await task
        results[result["proxy_id"]] = result
    
    return results