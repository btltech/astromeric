"""
config.py
---------
Centralized configuration for CSP, security headers, and app settings.
Supports .env-driven customization to avoid hardcoding sensitive URLs.
"""

import os
from typing import Dict, List

# ============================================================================
# CONTENT SECURITY POLICY (CSP) CONFIGURATION
# ============================================================================

class CSPConfig:
    """Dynamic CSP builder from environment variables."""
    
    # Defaults (most restrictive)
    DEFAULT_CSP = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
    }
    
    # Environment-based overrides
    ENV_OVERRIDES = {
        "CSP_SCRIPT_SRC": "script-src",
        "CSP_STYLE_SRC": "style-src",
        "CSP_CONNECT_SRC": "connect-src",
        "CSP_FONT_SRC": "font-src",
        "CSP_IMG_SRC": "img-src",
    }
    
    @classmethod
    def build(cls) -> Dict[str, List[str]]:
        """Build CSP directives from defaults + env overrides."""
        csp = {k: v.copy() for k, v in cls.DEFAULT_CSP.items()}
        
        # Apply environment overrides
        for env_var, directive in cls.ENV_OVERRIDES.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Parse space-separated URLs/values
                values = [v.strip() for v in env_value.split() if v.strip()]
                csp[directive] = values
        
        return csp
    
    @classmethod
    def to_header_string(cls) -> str:
        """Convert CSP dict to HTTP header string."""
        csp = cls.build()
        directives = []
        for directive, values in csp.items():
            directive_str = f"{directive} {' '.join(values)}"
            directives.append(directive_str)
        return "; ".join(directives)


# ============================================================================
# SECURITY HEADERS
# ============================================================================

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": CSPConfig.to_header_string(),
}


# ============================================================================
# DEFAULT CSP VALUES (for documentation and static .env templates)
# ============================================================================

DEFAULT_ENV_CSP_VALUES = {
    "CSP_SCRIPT_SRC": "'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com",
    "CSP_STYLE_SRC": "'self' 'unsafe-inline' https://api.fontshare.com https://fonts.googleapis.com",
    "CSP_FONT_SRC": "'self' https://api.fontshare.com https://cdn.fontshare.com https://fonts.gstatic.com https://fonts.googleapis.com",
    "CSP_CONNECT_SRC": (
        "'self' https://api.fontshare.com https://cdn.fontshare.com "
        "https://astromeric.com https://www.astromeric.com "
        "https://astronumeric.com https://www.astronumeric.com "
        "https://astromeric-backend-production.up.railway.app "
        "https://nominatim.openstreetmap.org "
        "https://api.openai.com https://generativelanguage.googleapis.com"
    ),
    "CSP_IMG_SRC": "'self' data: https:",
}
