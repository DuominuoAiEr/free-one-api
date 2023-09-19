import abc

import quart

from ..database import db


class APIGroup(metaclass=abc.ABCMeta):
    
    group_name: str
    """Name of this group, also the path prefix of all APIs in this group.
    
    e.g. /api
    """
    
    tokens: list[str]
    """Tokens for this group."""
    
    routers: list[tuple[str, list[str], callable, dict]]
    
    dbmgr: db.DatabaseInterface
    
    def set_tokens(self, tokens: list[str]):
        """Set tokens for this group.
        
        Args:
            tokens: tokens.
        """
        self.tokens = tokens
    
    def api(self, path: str, methods: list[str], auth: bool=False, **kwargs):
        """Register an API.
        
        Args:
            path: path of this API, relative to this group.
            methods: HTTP methods.
            **kwargs: other arguments.
        """

        def decorator(handler):
            """Decorator."""
            
            new_handler = handler
            if auth:
                async def authenticated_handler(*args, **kwargs):
                    """Authenticated handler."""
                    auth = quart.request.headers.get("Authorization")
                    if auth is None:
                        return quart.jsonify({
                            "code": 1,
                            "message": "No authorization provided."
                        })
                    if not auth.startswith("Bearer "):
                        return quart.jsonify({
                            "code": 2,
                            "message": "Wrong authorization type."
                        })
                    token = auth[7:]
                    if token not in self.tokens:
                        return quart.jsonify({
                            "code": 3,
                            "message": "Wrong token, please re-login."
                        })
                    return await handler(*args, **kwargs)
                new_handler = authenticated_handler
                new_handler.__name__ = handler.__name__
            
            self.routers.append((self.group_name+path, methods, new_handler, kwargs))
            return new_handler

        return decorator

    def __init__(self, dbmgr: db.DatabaseInterface):
        self.routers = []
        self.dbmgr = dbmgr
        
    def get_routers(self):
        """Get all APIs in this group.
        
        Returns:
            list of APIs.
        """
        return self.routers