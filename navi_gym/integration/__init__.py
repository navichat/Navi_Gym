"""
Integration module for customer system interfaces.

This module handles integration with existing customer systems including:
- API bridges for customer applications
- Chat system integration
- TTS and audio integration  
- Deployment infrastructure
"""

# Import key classes to make them available at integration level
try:
    from .customer_api import CustomerAPIBridge, CustomerRequest, AvatarResponse
except ImportError:
    # Module not yet fully implemented
    CustomerAPIBridge = None
    CustomerRequest = None
    AvatarResponse = None

__all__ = [
    'CustomerAPIBridge',
    'CustomerRequest', 
    'AvatarResponse',
]
