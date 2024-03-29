"""
This module provides functions for active session store.
"""
from typing import Dict, List, Optional
from datetime import datetime
from aiocache import SimpleMemoryCache
from .schemas import SessionInfo

# Use memory cache to store active user sessions
# key: {user_id}{session_id}
# value: SessionInfo
cache = SimpleMemoryCache()

async def add(user_id: str, session_id: str, value: SessionInfo, ttl: int) -> bool:
    """
    Add a user session to the cache store.

    Args:
        user_id (str): The ID of the user.
        session_id (str): The ID of the user session.
        value (SessionInfo): The SessionInfo object.
        ttl (int): The time-to-live (TTL) for the user session in seconds.

    Returns:
        bool: True if the session was successfully added to the store, False otherwise.
    """
    print(f"Adding session '{user_id}:{session_id}' to session store, TTL: {ttl} seconds")
    return await cache.add(key=session_id, value=value, namespace=user_id, ttl=ttl)

async def exists(user_id: str, session_id: str) -> bool:
    """
    Checks if a user session exists in the cache store.

    Args:
        user_id (str): The ID of the user.
        session_id (str): The ID of the user session.

    Returns:
        bool: True if the user session exists, False otherwise.
    """
    return await cache.exists(key=session_id, namespace=user_id)

async def retrieve(user_id: str, session_id: str) -> Optional[SessionInfo]:
    """
    Retrieve a user session from the cache store.

    Args:
        user_id (str): The ID of the user.
        session_id (str): The ID of the user session.

    Returns:
        Optional[SessionInfo]: The SessionInfo object if the session exists, None otherwise.
    """
    return await cache.get(key=session_id, namespace=user_id)

async def retrieve_by_userid(
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


async def update(user_id: str, session_id: str, data: dict, ttl: Optional[int] = None) -> bool:
    """
    Update a session in the session store with the provided data.

    Args:
        user_id (str): The ID of the user associated with the session.
        session_id (str): The ID of the session to update.
        data (dict): The data to update the session with.
        ttl (Optional[int]): The time-to-live (TTL) for the session in seconds.

    Returns:
        bool: True if the session was successfully updated, False otherwise.

    Usage:
        This function is used to update the data of a specific session in the session store.
        The `user_id` and `session_id` are used to identify the session, and the `data`
        dictionary contains the new data for the session. The `ttl` parameter is optional
        and specifies the new TTL for the session in seconds.

        Example:
            ```python
            user_id = "15b224ea-0b13-4530-8b0f-6986ded87a86"
            session_id = "f9bf5c3b-ad70-4c62-bb4b-7db250182a23"
            data = {"user_agent": "Mozilla/5.0", "last_active": datetime.utcnow() }
            ttl = 3600  # 1 hour

            success = await update(user_id, session_id, data, ttl)
            if success:
                print("Session updated successfully")
            else:
                print("Failed to update session")
    """
    session_info = await retrieve(user_id, session_id)

    if session_info is None:
        return False

    # update session_info with data
    for key, value in data.items():
        setattr(session_info, key, value)

    if ttl:
        print(f"Updating session '{user_id}:{session_id}' in session store, TTL: {ttl} seconds")
        return await cache.set(key=session_id, value=session_info, ttl=ttl, namespace=user_id)

    print(f"Updating session '{user_id}:{session_id}' in session store")
    return await cache.set(key=session_id, value=session_info, namespace=user_id)

async def update_ttl(user_id: str, session_id: str, ttl: int) -> bool:
    """
    Update the time-to-live (TTL) of a user session in the cache store.

    Args:
        user_id (str): The ID of the user.
        session_id (str): The ID of the user session.
        ttl (int): number of seconds for expiration. If 0, ttl is disabled

    Returns:
        bool: True if the session TTL was successfully updated, False otherwise.
    """
    print(f"Updating TTL of session '{user_id}:{session_id}' in session store")
    return await cache.expire(key=session_id, namespace=user_id, ttl=ttl)

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
        print(f"Removing session '{user_id}:{session_id}' from session store")

        # delete the specific user session of the user
        result = await cache.delete(key=session_id, namespace=user_id)

    else:
        # delete all sessions of the user
        sessions = await retrieve_by_userid(user_id=user_id, sort=False)
        for session in sessions[user_id]:
            print(f"Removing session '{user_id}:{session.session_id}' from session store")
            result += await cache.delete(key=session.session_id, namespace=user_id)

    return result
