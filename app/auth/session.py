from typing import Dict, List, Optional
from datetime import datetime
from aiocache import SimpleMemoryCache
from .schemas import SessionInfo

# Use memory cache to store active user sessions
# key: {user_id}{session_id}
# value: SessionInfo
cache = SimpleMemoryCache()

async def add(user_id: str, session_id: str, value, ttl: int) -> bool:
    """
    Add a user session to the cache.

    Args:
        user_id (str): The ID of the user.
        session_id (str): The ID of the user session.
        value (Any): The value object.
        ttl (int): The time-to-live (TTL) for the user session in seconds.

    Returns:
        bool: True if the session was successfully added to the cache, False otherwise.
    """
    return await cache.add(key=session_id, value=value, namespace=user_id, ttl=ttl)

async def exists(user_id: str, session_id: str) -> bool:
    """
    Checks if a user session exists in the cache.

    Args:
        user_id (str): The ID of the user.
        session_id (str): The ID of the user session.

    Returns:
        bool: True if the user session exists, False otherwise.
    """
    return await cache.exists(key=session_id, namespace=user_id)

async def update_last_activity(payload: dict):
    """
    Update the last activity timestamp of the user session.

    This function retrieves the user session from the cache using the user ID and session ID
    from the payload. If the session exists, it updates the last activity timestamp to the
    current time and saves the updated session back to the cache.

    Args:
        payload (dict): The payload of the token, which should include 'sub' (subject,
        representing the user ID) and 'sid' (session ID).

    """
    # Retrieve the user ID & session ID from the payload
    user_id = payload.get("sub")
    session_id = payload.get("sid")

    # Check if the session exists in the cache
    if not await cache.exists(key=session_id, namespace=user_id):
        # If the session does not exist, return
        return

    # Get the session info from the cache
    value: SessionInfo = await cache.get(key=session_id, namespace=user_id)

    # Update the last active timestamp to the current time
    value.last_active = datetime.utcnow()

    # Save the updated session info back to the cache
    await cache.set(key=session_id, namespace=user_id, value=value)

async def remove(user_id: str, session_id: Optional[str] = None) -> int:
    """
    Remove sessions based on the provided user_id and session_id.

    Args:
        user_id (str): The ID of the user.
        session_id (Optional[str]): The ID of the user session. If not provided,
        all sessions of the user will be removed.

    Returns:
        int: The number of sessions removed.
    """
    if not user_id:
        raise ValueError("user_id must be provided")

    result = 0

    if session_id:
        # delete the specific user session of the user
        result = await cache.delete(key=session_id, namespace=user_id)

    else:
        # delete all sessions of the user
        sessions = await retrieve_sessions_by_userid(user_id=user_id, sort=False)
        for session in sessions[user_id]:
            result += await cache.delete(key=session.session_id, namespace=user_id)

    return result

async def retrieve_sessions_by_userid(
    user_id: Optional[str] = None,
    sort: bool = True) -> Dict[str, List[SessionInfo]]:
    """
    Get user session(s), grouped by user id.

    Args:
        user_id (Optional[str]): The ID of the user. If None, all user sessions will be returned.
        Defaults to None
        sort (bool): Whether or not to sort the user sessions by last active time in descending order.
        Defaults is True.

    Returns:
        Dict[str, List[SessionInfo]]: A dictionary of sessions, grouped by user ID. Each user ID
        maps to a list of SessionInfo objects.
    """
    # Access the underlying cache object
    c = cache._cache # key: {user_id}{session_id}, value: SessionInfo

    # Initialize an empty dictionary to hold the sessions
    # Key: user_id, Value: list of SessionInfo
    sessions = {}

    # Iterate over all items in the cache
    for key, value in c.items():
        # If no user_id is provided or if the key starts with the provided user_id
        if user_id is None or key.startswith(user_id):
            # Extract the user_id from the key
            user_id = key[:36]
            # If the user_id is not already in the sessions dictionary, add it
            if user_id not in sessions:
                sessions[user_id] = []
            # Append the session to the list of sessions for this user_id
            sessions[user_id].append(value)

    # If sort is True, sort the sessions for each user_id
    if sort:
        for user_id in sessions:
            # Sort the sessions by last_active time in descending order
            sessions[user_id] = sorted(sessions[user_id],
                                       key=lambda session: session.last_active, reverse=True)

    # Return the dictionary of sessions
    return sessions