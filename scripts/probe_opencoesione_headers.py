"""Probe OpenCoesione ZIP headers without downloading CSV rows.

The probe requests only a bounded byte range from the public ZIP. It aborts before
reading the response body unless the server honors the Range request with HTTP 206.
From the returned ZIP prefix it decompresses only enough data to reach the first CSV
line break. No data rows are parsed or emitted.
"""

from __future__ import annotations

import argparse
import struct
import zlib
from dataclasses import dataclass
from typing import Final

import httpx

from procrun.collectors.opencoesione import EXPECTED_HEADERS

PUBLICATION_PAGE: Final = (
    "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
)
RANGE_END: Final = 262_143


class HeaderProbeError(RuntimeError):
    """Raised when a bounded header-only probe cannot be completed safely."""


@dataclass(frozen=True)
class ProbeResult:
    requested_url: str
    final_url: str
    content_range: str
    csv_member: str
    header: tuple[str, ...]


def _extract_csv_header_from_zip_prefix(prefix: bytes) -> tuple[str, tuple[str, ...]]:
    if len(prefix) < 30 or prefix[:4] != b"PK\x03\x04":
        raise HeaderProbeError("ZIP prefix does not begin with a local file header")

    (
        _signature,
        _version,
        flags,
        compression_method,
        _mtime,
        _mdate,
        _crc32,
        _compressed_size,
        _uncompressed_size,
        filename_length,
        extra_length,
    ) = struct.unpack("<IHHHHHIIIHH", prefix[:30])

    if flags & 0x1:
        raise HeaderProbeError("encrypted ZIP member is outside the approved contract")

    data_offset = 30 + filename_length + extra_length
    if len(prefix) <= data_offset:
        raise HeaderProbeError("bounded range is too small to reach ZIP member data")

    filename_end = 30 + filename_length
    try:
        member_name = prefix[30:filename_end].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HeaderProbeError("ZIP member name is not UTF-8") from exc
    if not member_name.lower().endswith(".csv"):
        raise HeaderProbeError(f"first ZIP member is not CSV: {member_name!r}")

    compressed_prefix = prefix[data_offset:]
    if compression_method == 0:
        csv_prefix = compressed_prefix
    elif compression_method == 8:
        decompressor = zlib.decompressobj(-15)
        try:
            csv_prefix = decompressor.decompress(compressed_prefix, 65_536)
        except zlib.error as exc:
            raise HeaderProbeError("could not decompress bounded ZIP prefix") from exc
    else:
        raise HeaderProbeError(
            f"unsupported ZIP compression method in header probe: {compression_method}"
        )

    newline = csv_prefix.find(b"\n")
    if newline < 0:
        raise HeaderProbeError("bounded range did not contain a complete CSV header line")

    header_bytes = csv_prefix[:newline].rstrip(b"\r")
    try:
        header_line = header_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HeaderProbeError("CSV header is not UTF-8") from exc
    header = tuple(part.strip() for part in header_line.split(";"))
    if not header or any(not field for field in header):
        raise HeaderProbeError("CSV header contains an empty field name")
    return member_name, header


def probe_header(url: str, *, timeout_seconds: float = 30.0) -> ProbeResult:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": "application/zip,application/octet-stream;q=0.9,*/*;q=0.1",
        "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
        "Referer": PUBLICATION_PAGE,
        "Range": f"bytes=0-{RANGE_END}",
    }
    with (
        httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client,
        client.stream("GET", url, headers=headers) as response,
    ):
        if response.status_code != 206:
            raise HeaderProbeError(
                "server did not honor bounded Range request; refusing to read response body "
                f"(status={response.status_code}, final_url={response.url})"
            )
        content_range = response.headers.get("content-range", "")
        expected_prefix = f"bytes 0-{RANGE_END}/"
        if not content_range.startswith(expected_prefix):
            raise HeaderProbeError(
                f"unexpected Content-Range for bounded probe: {content_range!r}"
            )
        prefix = b"".join(response.iter_bytes())
        final_url = str(response.url)

    if len(prefix) > RANGE_END + 1:
        raise HeaderProbeError("server returned more bytes than the bounded range")
    member_name, header = _extract_csv_header_from_zip_prefix(prefix)
    return ProbeResult(
        requested_url=url,
        final_url=final_url,
        content_range=content_range,
        csv_member=member_name,
        header=header,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--require-frozen-header", action="store_true")
    args = parser.parse_args()
    result = probe_header(args.url)
    print(f"requested_url={result.requested_url}")
    print(f"final_url={result.final_url}")
    print(f"content_range={result.content_range}")
    print(f"csv_member={result.csv_member}")
    print(f"header_count={len(result.header)}")
    if args.require_frozen_header and result.header != EXPECTED_HEADERS:
        missing = [field for field in EXPECTED_HEADERS if field not in result.header]
        unexpected = [field for field in result.header if field not in EXPECTED_HEADERS]
        raise HeaderProbeError(
            "header differs from frozen contract; "
            f"missing={missing!r}, unexpected={unexpected!r}, "
            f"order_changed={not missing and not unexpected}"
        )
    frozen_match = result.header == EXPECTED_HEADERS
    print(f"frozen_header_match={str(frozen_match).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
