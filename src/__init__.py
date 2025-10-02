"""Streamable.py - Unofficial Python wrapper for the Streamable.com API.

This package provides a comprehensive Python interface for interacting with
the undocumented Streamable.com API, enabling video uploads, account management,
and various other operations.

Example:
    Basic usage with the StreamableClient:

    ```python
    from streamable_py import StreamableClient, AccountInfo
    from pathlib import Path

    # Create account info
    account = AccountInfo(email="your@email.com", password="your_password")

    # Use the client
    with StreamableClient() as client:
        client.login(account)
        video = client.upload_video(Path("video.mp4"))
        print(f"Uploaded video: {video.url}")
    ```

Modules:
    api: Core API client and models for Streamable.com interaction
    utils: Utility functions for video processing and AWS S3 operations
"""
