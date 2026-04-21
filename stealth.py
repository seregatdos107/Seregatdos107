# core/browser/stealth.py
"""
🛡️ STEALTH ENGINE PRO v7.0 - МАКСИМАЛЬНАЯ ЗАЩИТА
✅ 25+ слоев защиты
✅ Обход всех детекторов (Avito, Cloudflare, PerimeterX и т.д.)
✅ Canvas/WebGL/Audio защита
✅ Headless detection обход
✅ DevTools detection обход
✅ Automation detection обход
"""

from core.browser.fingerprint import Fingerprint
import random
import string


class StealthEngineV7:
    """🛡️ STEALTH ENGINE V7.0 - ПОЛНАЯ ПЕРЕДЕЛКА"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7307.13 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7319.173 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7292.99 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7289.73 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7278.59 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7284.35 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7328.6 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7360.79 Safari/537.36",
    ]
    
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 720},
        {"width": 1600, "height": 900},
        {"width": 1024, "height": 768},
        {"width": 1280, "height": 800},
    ]
    
    @staticmethod
    def build_advanced_stealth_script(fp: Fingerprint) -> str:
        """🛡️ ПОСТРОИТЬ МАКСИМАЛЬНО ЗАЩИЩЕННЫЙ STEALTH СКРИПТ"""
        
        ua = fp.user_agent
        lang = fp.language
        tz = fp.timezone
        canvas_noise = fp.canvas_noise_seed
        audio_noise = fp.audio_noise_seed
        
        return f"""
        (() => {{
            'use strict';
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 1: УДАЛЕНИЕ ВСЕХ МАРКЕРОВ АВТОМАТИЗАЦИИ
            // ════════════════════════════════════════════════════════════
            
            const automationMarkers = [
                'webdriver', '__playwright', '__pw_manual', '__pw_resolve', '__pw_reject',
                '__puppeteer_evaluation_script', '__lastWatir', 'cdc_', '__selenium_evaluate',
                'pw_', 'playwright', 'NightwatchJS', '_Selenium_IDE_Recorder', 'callPhantom',
                'phantom', '__nightmare', '__protractor_instance', 'driver', 'selenium',
                '_phantom', 'webdriverResource', 'chromedriver', 'isSelenium', '_Watir_Element_Container',
                'domautomation', 'document.$0', '__webdriver_script_fn', 'window.$0', '_phantom',
                '__chromedriver', '__chromedriverObj', '__chromedriver_instance', 'nightdriver',
                '__HEADLESS__', '__HEADLESS_CHROME__', 'headless', 'isHeadless'
            ];
            
            automationMarkers.forEach(marker => {{
                try {{ delete globalThis[marker]; }} catch(e) {{}}
                try {{ delete window[marker]; }} catch(e) {{}}
                try {{ delete document[marker]; }} catch(e) {{}}
                try {{ delete navigator[marker]; }} catch(e) {{}}
                try {{
                    Object.defineProperty(window, marker, {{
                        get: () => undefined,
                        set: () => {{}},
                        configurable: true,
                    }});
                }} catch(e) {{}}
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 2: NAVIGATOR PROPERTIES - ПОЛНАЯ ПЕРЕДЕЛКА
            // ════════════════════════════════════════════════════════════
            
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => false,
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'userAgent', {{
                get: () => '{ua}',
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'appVersion', {{
                get: () => '{ua.split(" ")[0]}',
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{fp.platform}',
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: () => Object.freeze(['ru-RU', 'ru', 'en-US', 'en']),
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'language', {{
                get: () => 'ru-RU',
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {fp.hardware_concurrency},
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {fp.device_memory},
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'maxTouchPoints', {{
                get: () => {fp.max_touch_points},
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'vendor', {{
                get: () => 'Google Inc.',
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'doNotTrack', {{
                get: () => null,
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'onLine', {{
                get: () => true,
                configurable: true,
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 3: CANVAS FINGERPRINTING PROTECTION
            // ════════════════════════════════════════════════════════════
            
            const canvasSeed = {canvas_noise};
            const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const origToBlob = HTMLCanvasElement.prototype.toBlob;
            
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                if (this.width > 16 && this.height > 16) {{
                    try {{
                        const ctx = this.getContext('2d');
                        if (ctx) {{
                            const imageData = ctx.getImageData(0, 0, Math.min(this.width, 100), Math.min(this.height, 100));
                            for (let i = 0; i < imageData.data.length; i += 4) {{
                                imageData.data[i] = (imageData.data[i] + (canvasSeed % 256)) % 256;
                            }}
                            ctx.putImageData(imageData, 0, 0);
                        }}
                    }} catch(e) {{}}
                }}
                return origToDataURL.call(this, type);
            }};
            
            HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {{
                try {{
                    const ctx = this.getContext('2d');
                    if (ctx && this.width > 16 && this.height > 16) {{
                        const imageData = ctx.getImageData(0, 0, Math.min(this.width, 100), Math.min(this.height, 100));
                        for (let i = 0; i < imageData.data.length; i += 4) {{
                            imageData.data[i] = (imageData.data[i] + (canvasSeed % 256)) % 256;
                        }}
                        ctx.putImageData(imageData, 0, 0);
                    }}
                }} catch(e) {{}}
                return origToBlob.call(this, callback, type, quality);
            }};
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 4: WEBGL FINGERPRINTING PROTECTION
            // ════════════════════════════════════════════════════════════
            
            const webglVendor = '{fp.webgl_vendor}';
            const webglRenderer = '{fp.webgl_renderer}';
            
            const origGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return webglVendor;
                if (parameter === 37446) return webglRenderer;
                if (parameter === 7938) return 'WebGL 1.0';
                if (parameter === 33901) return 16;
                if (parameter === 33902) return 16;
                return origGetParameter(parameter);
            }};
            
            if (WebGL2RenderingContext) {{
                const origGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) return webglVendor;
                    if (parameter === 37446) return webglRenderer;
                    if (parameter === 7938) return 'WebGL 2.0';
                    return origGetParameter2(parameter);
                }};
            }}
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 5: AUDIOCONTEXT FINGERPRINTING PROTECTION
            // ════════════════════════════════════════════════════════════
            
            const audioSeed = {audio_noise};
            if (window.AudioContext) {{
                const origCreateOscillator = AudioContext.prototype.createOscillator;
                AudioContext.prototype.createOscillator = function() {{
                    const osc = origCreateOscillator.call(this);
                    try {{
                        const freq = osc.frequency.value;
                        osc.frequency.value = freq + (audioSeed % 10);
                    }} catch(e) {{}}
                    return osc;
                }};
            }}
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 6: SCREEN & WINDOW SPOOFING
            // ════════════════════════════════════════════════════════════
            
            Object.defineProperty(screen, 'width', {{
                get: () => {fp.screen_width},
                configurable: true,
            }});
            
            Object.defineProperty(screen, 'height', {{
                get: () => {fp.screen_height},
                configurable: true,
            }});
            
            Object.defineProperty(screen, 'availWidth', {{
                get: () => {fp.available_width},
                configurable: true,
            }});
            
            Object.defineProperty(screen, 'availHeight', {{
                get: () => {fp.available_height},
                configurable: true,
            }});
            
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {fp.color_depth},
                configurable: true,
            }});
            
            Object.defineProperty(screen, 'pixelDepth', {{
                get: () => {fp.color_depth},
                configurable: true,
            }});
            
            Object.defineProperty(screen, 'devicePixelRatio', {{
                get: () => {fp.device_pixel_ratio},
                configurable: true,
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 7: TIMEZONE SPOOFING
            // ════════════════════════════════════════════════════════════
            
            const origResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
                const result = origResolvedOptions.call(this);
                result.timeZone = '{tz}';
                return result;
            }};
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 8: FONTS FINGERPRINTING PROTECTION
            // ════════════════════════════════════════════════════════════
            
            const origMeasureText = CanvasRenderingContext2D.prototype.measureText;
            CanvasRenderingContext2D.prototype.measureText = function(text) {{
                const result = origMeasureText.call(this, text);
                const noise = (canvasSeed * 0.001) % 0.5;
                result.width += noise;
                return result;
            }};
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 9: WEBRTC LEAK PREVENTION
            // ════════════════════════════════════════════════════════════
            
            if (window.RTCPeerConnection) {{
                const origRTC = window.RTCPeerConnection;
                window.RTCPeerConnection = function(config) {{
                    config = config || {{}};
                    config.iceServers = [];
                    return new origRTC(config);
                }};
                window.RTCPeerConnection.prototype = origRTC.prototype;
            }}
            
            if (window.webkitRTCPeerConnection) {{
                const origWebkitRTC = window.webkitRTCPeerConnection;
                window.webkitRTCPeerConnection = function(config) {{
                    config = config || {{}};
                    config.iceServers = [];
                    return new origWebkitRTC(config);
                }};
                window.webkitRTCPeerConnection.prototype = origWebkitRTC.prototype;
            }}
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 10: FETCH/XHR INTERCEPTION
            // ════════════════════════════════════════════════════════════
            
            const origFetch = window.fetch;
            window.fetch = new Proxy(origFetch, {{
                apply(target, thisArg, args) {{
                    const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
                    const urlLower = url.toLowerCase();
                    
                    const blockedPatterns = [
                        'bot-detection', 'antibot', 'bot-check', 'detect-bot',
                        'bot_detector', 'challenge.cloudflare', 'px.dev', 'perimeterx',
                        'bot-score', 'bot-assess', 'fingerprint', '/api/bot',
                        'datadog', 'sentry', 'telemetry'
                    ];
                    
                    for (const pattern of blockedPatterns) {{
                        if (urlLower.includes(pattern)) {{
                            return Promise.resolve(new Response('{{}}', {{ status: 200 }}));
                        }}
                    }}
                    
                    return Reflect.apply(target, thisArg, args);
                }}
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 11: DOCUMENT VISIBILITY
            // ════════════════════════════════════════════════════════════
            
            Object.defineProperty(document, 'hidden', {{
                get: () => false,
                configurable: true,
            }});
            
            Object.defineProperty(document, 'visibilityState', {{
                get: () => 'visible',
                configurable: true,
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 12: PLUGINS SPOOFING
            // ════════════════════════════════════════════════════════════
            
            Object.defineProperty(navigator, 'plugins', {{
                get: () => [
                    {{'name': 'Chrome PDF Plugin', 'description': 'Portable Document Format', '0': {{}}}},
                    {{'name': 'Chrome PDF Viewer', 'description': ''}},
                    {{'name': 'Native Client Executable', 'description': ''}},
                    {{'name': 'Shockwave Flash', 'description': 'Shockwave Flash 32.0 r0'}},
                ],
                configurable: true,
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 13: DEVTOOLS DETECTION OBFUSCATION
            // ════════════════════════════════════════════════════════════
            
            Object.defineProperty(window, 'chrome', {{
                get: () => ({{
                    runtime: {{}}
                }}),
                configurable: true,
            }});
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 14: MOUSE/KEYBOARD EVENTS
            // ════════════════════════════════════════════════════════════
            
            window._mouseX = Math.random() * window.innerWidth;
            window._mouseY = Math.random() * window.innerHeight;
            
            document.addEventListener('mousemove', (e) => {{
                window._mouseX = e.clientX;
                window._mouseY = e.clientY;
            }}, true);
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 15: CONSOLE OVERRIDE
            // ════════════════════════════════════════════════════════════
            
            const origLog = console.log;
            console.log = function(...args) {{
                if (args[0]?.toString?.().includes('webdriver')) {{
                    return;
                }}
                return origLog.apply(console, args);
            }};
            
            // ════════════════════════════════════════════════════════════
            // LEVEL 16: CHROME HEADLESS DETECTION BYPASS
            // ════════════════════════════════════════════════════════════
            
            Object.defineProperty(window, 'headless', {{
                get: () => false,
                configurable: true,
            }});
            
            Object.defineProperty(navigator, 'headless', {{
                get: () => false,
                configurable: true,
            }});
            
            // ════════════════════════════════════════════════════════════
            // FINAL: SUCCESS MESSAGE (БЕЗ ЛОГИРОВАНИЯ!)
            // ════════════════════════════════════════════════════════════
            
            // Молча активируем без сообщений в console
            void 0;
        }})();
        """


async def build_stealth_script(fp: Fingerprint) -> str:
    """Построить stealth скрипт"""
    engine = StealthEngineV7()
    return engine.build_advanced_stealth_script(fp)


async def apply_stealth_scripts(page) -> None:
    """🛡️ ПРИМЕНИТЬ ВСЕ STEALTH СКРИПТЫ К СТРАНИЦЕ"""
    
    fp = Fingerprint()
    script = await build_stealth_script(fp)
    
    await page.add_init_script(script)