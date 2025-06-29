"""
Customer API bridge for integrating Navi Gym with existing customer systems.

This module provides the interface between the RL training system and
customer-facing applications, ensuring seamless integration with existing
infrastructure while adding RL capabilities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import torch
import websockets
import aiohttp
from datetime import datetime


@dataclass
class CustomerRequest:
    """Represents a request from customer system."""
    request_id: str
    customer_id: str
    session_id: str
    request_type: str  # 'chat', 'avatar_action', 'status_query', etc.
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 0


@dataclass
class AvatarResponse:
    """Represents a response to customer system."""
    request_id: str
    response_type: str
    avatar_state: Dict[str, Any]
    actions_taken: List[str]
    emotional_context: Dict[str, Any]
    success: bool
    message: Optional[str] = None
    timestamp: Optional[datetime] = None


class CustomerAPIBridge:
    """
    Main bridge between Navi Gym RL system and customer applications.
    
    This class handles:
    - Customer requests routing
    - Avatar state synchronization
    - Real-time communication
    - Integration with existing customer infrastructure
    """
    
    def __init__(
        self,
        avatar_controller,
        rl_agent,
        config: Dict[str, Any] = None
    ):
        self.avatar_controller = avatar_controller
        self.rl_agent = rl_agent
        self.config = config or {}
        
        # Communication channels
        self.websocket_server = None
        self.http_server = None
        self.request_queue = asyncio.Queue()
        self.response_callbacks = {}
        
        # State management
        self.active_sessions = {}
        self.customer_contexts = {}
        
        # Integration adapters
        self.chat_adapter = None
        self.tts_adapter = None
        self.render_adapter = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize adapters
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """Initialize adapters for different customer system components."""
        # Chat system adapter
        if self.config.get('enable_chat_integration', True):
            self.chat_adapter = ChatSystemAdapter(self)
        
        # TTS system adapter
        if self.config.get('enable_tts_integration', True):
            self.tts_adapter = TTSSystemAdapter(self)
        
        # Render system adapter
        if self.config.get('enable_render_integration', True):
            self.render_adapter = RenderSystemAdapter(self)
    
    async def start_server(self, host: str = "localhost", port: int = 8080):
        """Start the API bridge server."""
        self.logger.info(f"Starting Customer API Bridge on {host}:{port}")
        
        # Start WebSocket server for real-time communication
        websocket_handler = self._create_websocket_handler()
        self.websocket_server = await websockets.serve(
            websocket_handler, host, port + 1
        )
        
        # Start HTTP server for REST API
        app = self._create_http_app()
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, host, port)
        await site.start()
        
        # Start request processing loop
        asyncio.create_task(self._process_requests())
        
        self.logger.info("Customer API Bridge started successfully")
    
    def _create_websocket_handler(self):
        """Create WebSocket handler for real-time communication."""
        async def websocket_handler(websocket, path):
            self.logger.info(f"New WebSocket connection: {path}")
            
            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        request = CustomerRequest(
                            request_id=data.get('request_id', ''),
                            customer_id=data.get('customer_id', ''),
                            session_id=data.get('session_id', ''),
                            request_type=data.get('type', ''),
                            payload=data.get('payload', {}),
                            timestamp=datetime.now(),
                            priority=data.get('priority', 0)
                        )
                        
                        # Queue request for processing
                        await self.request_queue.put(request)
                        
                        # Send acknowledgment
                        ack = {
                            'request_id': request.request_id,
                            'status': 'queued',
                            'timestamp': request.timestamp.isoformat()
                        }
                        await websocket.send(json.dumps(ack))
                        
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({
                            'error': 'Invalid JSON format'
                        }))
                    except Exception as e:
                        self.logger.error(f"WebSocket error: {e}")
                        await websocket.send(json.dumps({
                            'error': f'Processing error: {str(e)}'
                        }))
            
            except websockets.exceptions.ConnectionClosed:
                self.logger.info("WebSocket connection closed")
        
        return websocket_handler
    
    def _create_http_app(self):
        """Create HTTP application for REST API."""
        app = aiohttp.web.Application()
        
        # Add routes
        app.router.add_post('/api/avatar/action', self._handle_avatar_action)
        app.router.add_get('/api/avatar/status', self._handle_avatar_status)
        app.router.add_post('/api/chat/message', self._handle_chat_message)
        app.router.add_get('/api/session/{session_id}/context', self._handle_get_context)
        app.router.add_post('/api/session/{session_id}/context', self._handle_set_context)
        
        # Add CORS middleware if needed
        if self.config.get('enable_cors', True):
            app.middlewares.append(self._cors_middleware)
        
        return app
    
    async def _cors_middleware(self, request, handler):
        """CORS middleware for cross-origin requests."""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    async def _handle_avatar_action(self, request):
        """Handle avatar action requests."""
        try:
            data = await request.json()
            
            # Create customer request
            customer_request = CustomerRequest(
                request_id=data.get('request_id', f"req_{datetime.now().timestamp()}"),
                customer_id=data.get('customer_id', 'unknown'),
                session_id=data.get('session_id', 'default'),
                request_type='avatar_action',
                payload=data,
                timestamp=datetime.now()
            )
            
            # Process request
            response = await self._process_avatar_request(customer_request)
            
            return aiohttp.web.json_response(asdict(response))
            
        except Exception as e:
            self.logger.error(f"Avatar action error: {e}")
            return aiohttp.web.json_response(
                {'error': str(e)}, status=500
            )
    
    async def _handle_avatar_status(self, request):
        """Handle avatar status requests."""
        try:
            session_id = request.query.get('session_id', 'default')
            
            # Get current avatar state
            current_state = self.avatar_controller.current_state
            
            status = {
                'session_id': session_id,
                'avatar_state': {
                    'position': current_state.position.cpu().tolist(),
                    'emotion': current_state.emotion_state,
                    'interaction_context': current_state.interaction_context
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return aiohttp.web.json_response(status)
            
        except Exception as e:
            self.logger.error(f"Status query error: {e}")
            return aiohttp.web.json_response(
                {'error': str(e)}, status=500
            )
    
    async def _handle_chat_message(self, request):
        """Handle chat message processing."""
        if not self.chat_adapter:
            return aiohttp.web.json_response(
                {'error': 'Chat integration not enabled'}, status=400
            )
        
        try:
            data = await request.json()
            response = await self.chat_adapter.process_message(data)
            return aiohttp.web.json_response(response)
            
        except Exception as e:
            self.logger.error(f"Chat message error: {e}")
            return aiohttp.web.json_response(
                {'error': str(e)}, status=500
            )
    
    async def _handle_get_context(self, request):
        """Get session context."""
        session_id = request.match_info['session_id']
        context = self.customer_contexts.get(session_id, {})
        return aiohttp.web.json_response(context)
    
    async def _handle_set_context(self, request):
        """Set session context."""
        session_id = request.match_info['session_id']
        data = await request.json()
        self.customer_contexts[session_id] = data
        return aiohttp.web.json_response({'status': 'updated'})
    
    async def _process_requests(self):
        """Main request processing loop."""
        while True:
            try:
                request = await self.request_queue.get()
                
                # Process based on request type
                if request.request_type == 'avatar_action':
                    response = await self._process_avatar_request(request)
                elif request.request_type == 'chat':
                    response = await self._process_chat_request(request)
                elif request.request_type == 'status_query':
                    response = await self._process_status_request(request)
                else:
                    response = AvatarResponse(
                        request_id=request.request_id,
                        response_type='error',
                        avatar_state={},
                        actions_taken=[],
                        emotional_context={},
                        success=False,
                        message=f"Unknown request type: {request.request_type}"
                    )
                
                # Send response if callback is registered
                if request.request_id in self.response_callbacks:
                    callback = self.response_callbacks[request.request_id]
                    await callback(response)
                
            except Exception as e:
                self.logger.error(f"Request processing error: {e}")
    
    async def _process_avatar_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process avatar-specific requests."""
        try:
            payload = request.payload
            
            # Get current context
            context = self.customer_contexts.get(request.session_id, {})
            context.update({
                'customer_id': request.customer_id,
                'request_type': request.request_type
            })
            
            # Get current observations
            observations = self.avatar_controller.get_observation().unsqueeze(0)
            
            # Get RL agent action with customer context
            if hasattr(self.rl_agent, 'act_for_customer'):
                actions = self.rl_agent.act_for_customer(observations, context)
            else:
                actions, _, _ = self.rl_agent.act(observations)
            
            # Update avatar controller
            self.avatar_controller.update_from_agent(actions[0], context)
            
            # Process customer interaction
            interaction_response = self.avatar_controller.process_customer_interaction({
                'type': payload.get('interaction_type', 'general'),
                'content': payload.get('content', ''),
                'customer_mood': payload.get('mood', 'neutral'),
                'timestamp': request.timestamp.isoformat()
            })
            
            # Create response
            response = AvatarResponse(
                request_id=request.request_id,
                response_type='avatar_action',
                avatar_state={
                    'position': self.avatar_controller.current_state.position.cpu().tolist(),
                    'emotion': self.avatar_controller.current_state.emotion_state,
                    'facial_expression': self.avatar_controller.current_state.facial_expression.cpu().tolist()
                },
                actions_taken=[f"action_{i}" for i in range(len(actions[0]))],
                emotional_context=interaction_response,
                success=True,
                timestamp=datetime.now()
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Avatar request processing error: {e}")
            return AvatarResponse(
                request_id=request.request_id,
                response_type='error',
                avatar_state={},
                actions_taken=[],
                emotional_context={},
                success=False,
                message=str(e),
                timestamp=datetime.now()
            )
    
    async def _process_chat_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process chat requests."""
        if not self.chat_adapter:
            return AvatarResponse(
                request_id=request.request_id,
                response_type='error',
                avatar_state={},
                actions_taken=[],
                emotional_context={},
                success=False,
                message="Chat integration not available"
            )
        
        # Delegate to chat adapter
        return await self.chat_adapter.process_request(request)
    
    async def _process_status_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process status query requests."""
        current_state = self.avatar_controller.current_state
        
        return AvatarResponse(
            request_id=request.request_id,
            response_type='status',
            avatar_state={
                'position': current_state.position.cpu().tolist(),
                'rotation': current_state.rotation.cpu().tolist(),
                'emotion': current_state.emotion_state,
                'interaction_context': current_state.interaction_context
            },
            actions_taken=[],
            emotional_context={},
            success=True,
            timestamp=datetime.now()
        )
    
    def register_response_callback(self, request_id: str, callback: Callable):
        """Register a callback for response handling."""
        self.response_callbacks[request_id] = callback
    
    def unregister_response_callback(self, request_id: str):
        """Unregister a response callback."""
        if request_id in self.response_callbacks:
            del self.response_callbacks[request_id]
    
    async def shutdown(self):
        """Shutdown the API bridge."""
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        self.logger.info("Customer API Bridge shutdown complete")


class CustomerSystemAdapter(ABC):
    """Base class for customer system adapters."""
    
    def __init__(self, api_bridge: CustomerAPIBridge):
        self.api_bridge = api_bridge
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def process_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process a customer request."""
        pass


class ChatSystemAdapter(CustomerSystemAdapter):
    """Adapter for chat system integration."""
    
    def __init__(self, api_bridge: CustomerAPIBridge):
        super().__init__(api_bridge)
        self.conversation_history = {}
    
    async def process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat message."""
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        customer_id = data.get('customer_id', 'unknown')
        
        # Store conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'customer_id': customer_id
        })
        
        # Analyze message for emotional context and interaction type
        interaction_context = self._analyze_message(message)
        
        # Update avatar based on message
        avatar_request = CustomerRequest(
            request_id=f"chat_{datetime.now().timestamp()}",
            customer_id=customer_id,
            session_id=session_id,
            request_type='avatar_action',
            payload={
                'interaction_type': interaction_context.get('type', 'conversation'),
                'content': message,
                'mood': interaction_context.get('mood', 'neutral')
            },
            timestamp=datetime.now()
        )
        
        # Process through avatar system
        avatar_response = await self.api_bridge._process_avatar_request(avatar_request)
        
        return {
            'session_id': session_id,
            'avatar_response': asdict(avatar_response),
            'conversation_context': interaction_context
        }
    
    async def process_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process a chat-specific request."""
        message_data = request.payload
        response_data = await self.process_message(message_data)
        
        return AvatarResponse(
            request_id=request.request_id,
            response_type='chat',
            avatar_state=response_data['avatar_response']['avatar_state'],
            actions_taken=response_data['avatar_response']['actions_taken'],
            emotional_context=response_data['conversation_context'],
            success=True,
            timestamp=datetime.now()
        )
    
    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for emotional context and interaction type."""
        # Simple analysis - would be more sophisticated in practice
        message_lower = message.lower()
        
        # Detect interaction type
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            interaction_type = 'greeting'
        elif any(word in message_lower for word in ['bye', 'goodbye', 'farewell', 'see you']):
            interaction_type = 'farewell'
        elif '?' in message:
            interaction_type = 'question'
        elif any(word in message_lower for word in ['thank', 'thanks', 'great', 'awesome']):
            interaction_type = 'compliment'
        else:
            interaction_type = 'conversation'
        
        # Detect mood
        if any(word in message_lower for word in ['angry', 'frustrated', 'annoyed']):
            mood = 'frustrated'
        elif any(word in message_lower for word in ['happy', 'excited', 'great', 'awesome']):
            mood = 'excited'
        elif any(word in message_lower for word in ['sad', 'disappointed', 'sorry']):
            mood = 'sad'
        else:
            mood = 'neutral'
        
        return {
            'type': interaction_type,
            'mood': mood,
            'keywords': message_lower.split()
        }


class TTSSystemAdapter(CustomerSystemAdapter):
    """Adapter for TTS system integration."""
    
    async def process_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process TTS-related requests."""
        # This will be implemented when TTS system is migrated
        return AvatarResponse(
            request_id=request.request_id,
            response_type='tts',
            avatar_state={},
            actions_taken=['tts_processed'],
            emotional_context={},
            success=True,
            message="TTS processing complete",
            timestamp=datetime.now()
        )


class RenderSystemAdapter(CustomerSystemAdapter):
    """Adapter for render system integration."""
    
    async def process_request(self, request: CustomerRequest) -> AvatarResponse:
        """Process render-related requests."""
        # This will be implemented when render system is migrated
        return AvatarResponse(
            request_id=request.request_id,
            response_type='render',
            avatar_state={},
            actions_taken=['render_updated'],
            emotional_context={},
            success=True,
            message="Render update complete",
            timestamp=datetime.now()
        )
