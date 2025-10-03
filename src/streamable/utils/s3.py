"""AWS S3 Signature Version 4 utility for generating authentication headers.

This module provides functions to calculate AWS Signature V4 signatures
and build headers for S3 upload requests.

https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html
"""

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote
from ..api.models import UploadInfo


def _sign(key: bytes, msg: str) -> bytes:
    """Create HMAC-SHA256 signature.

    Args:
        key: The signing key
        msg: The message to sign

    Returns:
        HMAC-SHA256 digest
    """
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(
    secret_key: str, date_stamp: str, region: str, service: str
) -> bytes:
    """Derive the signing key for AWS Signature Version 4.

    Args:
        secret_key: AWS secret access key
        date_stamp: Date in YYYYMMDD format
        region: AWS region (e.g., 'us-east-1')
        service: AWS service name (e.g., 's3')

    Returns:
        Derived signing key
    """
    k_date: bytes = _sign(("AWS4" + secret_key).encode("utf-8"), date_stamp)
    k_region: bytes = _sign(k_date, region)
    k_service: bytes = _sign(k_region, service)
    k_signing: bytes = _sign(k_service, "aws4_request")
    return k_signing


def _uri_encode(s: str, encode_slash: bool = True) -> str:
    """URI encode according to AWS requirements.

    Args:
        s: String to encode
        encode_slash: Whether to encode forward slashes (True for query params, False for path)

    Returns:
        URI-encoded string
    """
    safe: str = "" if encode_slash else "/"
    encoded: str = quote(s, safe=safe + "-_.~")
    return encoded


def _create_canonical_request(
    method: str,
    canonical_uri: str,
    canonical_query_string: str,
    canonical_headers: str,
    signed_headers: str,
    payload_hash: str,
) -> str:
    """Create the canonical request string.

    Args:
        method: HTTP method (e.g., 'PUT', 'GET')
        canonical_uri: URI-encoded request path
        canonical_query_string: URI-encoded and sorted query string
        canonical_headers: Lowercase, sorted headers with values
        signed_headers: Semicolon-separated list of signed header names
        payload_hash: Hash of the request payload

    Returns:
        Canonical request string
    """
    return "\n".join(
        [
            method,
            canonical_uri,
            canonical_query_string,
            canonical_headers,
            signed_headers,
            payload_hash,
        ]
    )


def _create_string_to_sign(
    timestamp: str, credential_scope: str, canonical_request: str
) -> str:
    """Create the string to sign.

    Args:
        timestamp: ISO8601 timestamp (e.g., '20250929T151031Z')
        credential_scope: Scope string (date/region/service/aws4_request)
        canonical_request: The canonical request string

    Returns:
        String to sign
    """
    canonical_request_hash: str = hashlib.sha256(
        canonical_request.encode("utf-8")
    ).hexdigest()
    return "\n".join(
        ["AWS4-HMAC-SHA256", timestamp, credential_scope, canonical_request_hash]
    )


def calculate_aws_s3_v4_signature(
    method: str,
    host: str,
    path: str,
    access_key: str,
    secret_key: str,
    session_token: str,
    region: str,
    timestamp: str,
    payload_hash: str = "UNSIGNED-PAYLOAD",
    query_params: Optional[dict[str, str]] = None,
    extra_headers: Optional[dict[str, str]] = None,
) -> tuple[str, str, str]:
    """Calculate AWS S3 V4 signature.

    Args:
        method: HTTP method (e.g., 'PUT', 'GET')
        host: Host header value (e.g., 'streamables-upload.s3.amazonaws.com')
        path: Request path (e.g., '/upload/y3vwnh')
        access_key: AWS access key ID
        secret_key: AWS secret access key
        session_token: AWS session token
        region: AWS region (e.g., 'us-east-1')
        timestamp: ISO8601 timestamp (e.g., '20250929T151031Z')
        payload_hash: Hash of payload or 'UNSIGNED-PAYLOAD' (default)
        query_params: Optional query string parameters
        extra_headers: Optional additional headers to sign

    Returns:
        Tuple of (authorization_header, signed_headers, credential_scope)
    """
    # Extract date from timestamp (YYYYMMDD)
    date_stamp: str = timestamp[:8]

    # Create credential scope
    credential_scope: str = f"{date_stamp}/{region}/s3/aws4_request"

    # Prepare canonical URI (already URI-encoded path)
    canonical_uri: str = path

    # Prepare canonical query string
    canonical_query_string: str = ""
    if query_params:
        # Sort and encode query parameters
        sorted_params: list[tuple[str, str]] = sorted(query_params.items())
        encoded_params: list[str] = [
            f"{_uri_encode(k)}={_uri_encode(v)}" for k, v in sorted_params
        ]
        canonical_query_string = "&".join(encoded_params)

    # Prepare canonical headers - start with required headers
    headers: dict[str, str] = {
        "host": host,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": timestamp,
        "x-amz-security-token": session_token,
    }

    # Add any extra headers
    if extra_headers:
        headers.update({k.lower(): v for k, v in extra_headers.items()})

    # Sort headers and create canonical headers string
    sorted_headers: list[tuple[str, str]] = sorted(headers.items())
    canonical_headers: str = "".join([f"{k}:{v.strip()}\n" for k, v in sorted_headers])

    # Create signed headers string
    signed_headers: str = ";".join([k for k, _ in sorted_headers])

    # Create canonical request
    canonical_request: str = _create_canonical_request(
        method,
        canonical_uri,
        canonical_query_string,
        canonical_headers,
        signed_headers,
        payload_hash,
    )

    # Create string to sign
    string_to_sign: str = _create_string_to_sign(
        timestamp, credential_scope, canonical_request
    )

    # Calculate signing key
    signing_key: bytes = _get_signature_key(secret_key, date_stamp, region, "s3")

    # Calculate signature
    signature: str = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Create authorization header
    authorization_header: str = (
        f"AWS4-HMAC-SHA256 "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    return authorization_header, signed_headers, credential_scope


def build_s3_upload_headers(
    upload_info: UploadInfo,
    content_length: int,
    content_type: str = "application/octet-stream",
    use_current_timestamp: bool = True,
) -> dict[str, str]:
    """Build headers for S3 upload request from UploadInfo model.

    Args:
        upload_info: UploadInfo pydantic model instance
        content_length: Size of the file being uploaded in bytes
        content_type: MIME type of the content (default: 'application/octet-stream')
        use_current_timestamp: If True, generate a new timestamp (recommended for actual uploads)

    Returns:
        Dictionary of headers ready for the PUT request
    """
    # Extract necessary data from upload_info
    credentials = upload_info.credentials
    fields = upload_info.fields

    # Parse host from bucket name
    # Format: bucket-name.s3.amazonaws.com
    bucket: str = upload_info.bucket
    host: str = f"{bucket}.s3.amazonaws.com"

    # Extract path from key
    path: str = f"/{fields.key}"

    # Extract region from credential
    # Format: AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/s3/aws4_request
    credential_parts: list[str] = fields.X_Amz_Credential.split("/")
    region: str = credential_parts[2]

    # Use current timestamp or the one from fields
    if use_current_timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    else:
        timestamp = fields.X_Amz_Date

    # Calculate signature
    auth_header, _, _ = calculate_aws_s3_v4_signature(
        method="PUT",
        host=host,
        path=path,
        access_key=credentials.accessKeyId,
        secret_key=credentials.secretAccessKey,
        session_token=credentials.sessionToken,
        region=region,
        timestamp=timestamp,
        payload_hash="UNSIGNED-PAYLOAD",
        extra_headers={
            "x-amz-acl": fields.acl,
            "x-amz-user-agent": "aws-sdk-js/2.1530.0 callback",
        },
    )

    # Build headers dictionary
    headers: dict[str, str] = {
        "Host": host,
        "Authorization": auth_header,
        "Content-Type": content_type,
        "Content-Length": str(content_length),
        "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
        "x-amz-date": timestamp,
        "x-amz-security-token": credentials.sessionToken,
        "x-amz-acl": fields.acl,
        "x-amz-user-agent": "aws-sdk-js/2.1530.0 callback",
    }

    return headers
