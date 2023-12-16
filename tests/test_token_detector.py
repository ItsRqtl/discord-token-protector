import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io

import pytest

from src.utils.token_detection import TokenDetector


@pytest.mark.parametrize(
    "token, expected",
    [
        ("MTA3MjYyNTE0OTM3MjgxMzM1NA.ABCDEF.abcdefghijklmnopqrstuvwxyz123456", True),
        ("notavalidtokenbecauseitdoesnothaveperiods", False),
        ("badencoding.ABCDEF.abcdefghijklmnopqrstuvwxyz123456", False),
        ("", False),
        ("short.tok.en", False),
    ],
)
def test_validate(token, expected):
    result = TokenDetector.validate(token)
    assert result == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            "Text and a valid token MTA3MjYyNTE0OTM3MjgxMzM1NA.ABCDEF.abcdefghijklmnopqrstuvwxyz123456 in between",
            True,
        ),
        (
            "Text and a token with bad encoding badencoding.ABCDEF.abcdefghijklmnopqrstuvwxyz123456 in between",
            False,
        ),
        ("Just some random text without any token", False),
        (
            "Some random text and an invalid token notavalidtokenbecauseitdoesnothaveperiods somewhere in between",
            False,
        ),
        ("", False),
    ],
)
def test_detect(content, expected):
    result = TokenDetector.detect(content)
    assert result == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            b"Valid UTF-8 content with a token MTA3MjYyNTE0OTM3MjgxMzM1NA.ABCDEF.abcdefghijklmnopqrstuvwxyz123456",
            True,
        ),
        (b"\xff\xfe\xfd with some invalid UTF-8 bytes", False),
        (b"", False),
    ],
)
def test_decoder_search(data, expected):
    result = TokenDetector.decoder_search(data)
    assert result == expected


@pytest.mark.parametrize(
    "buffer, expected",
    [
        (open("tests/assets/plain/safe.txt", "rb").read(), False),
        (open("tests/assets/plain/danger.txt", "rb").read(), True),
    ],
)
def test_plain_text_decoder_search(buffer, expected):
    result = TokenDetector.decoder_search(buffer)
    assert result == expected


@pytest.mark.parametrize(
    "file_obj, expected",
    [
        (io.BytesIO(open("tests/assets/7zip/safe.7z", "rb").read()), False),
        (io.BytesIO(open("tests/assets/7zip/danger.7z", "rb").read()), True),
    ],
)
def test_scan_7z(file_obj, expected):
    result = TokenDetector.scan_7z(file_obj)
    assert result == expected


@pytest.mark.parametrize(
    "file_obj, expected",
    [
        (io.BytesIO(open("tests/assets/bzip2/safe.tar.bz2", "rb").read()), False),
        (io.BytesIO(open("tests/assets/bzip2/danger.tar.bz2", "rb").read()), True),
    ],
)
def test_scan_bzip2(file_obj, expected):
    result = TokenDetector.scan_bz2(file_obj)
    assert result == expected


@pytest.mark.parametrize(
    "file_obj, expected",
    [
        (io.BytesIO(open("tests/assets/gzip/safe.tar.gz", "rb").read()), False),
        (io.BytesIO(open("tests/assets/gzip/danger.tar.gz", "rb").read()), True),
    ],
)
def test_scan_gzip(file_obj, expected):
    result = TokenDetector.scan_gzip(file_obj)
    assert result == expected


@pytest.mark.parametrize(
    "file_obj, expected",
    [
        (io.BytesIO(open("tests/assets/rar/safe.rar", "rb").read()), False),
        (io.BytesIO(open("tests/assets/rar/danger.rar", "rb").read()), True),
    ],
)
def test_scan_rar(file_obj, expected):
    result = TokenDetector.scan_rar(file_obj)
    assert result == expected


@pytest.mark.parametrize(
    "file_obj, expected",
    [
        (io.BytesIO(open("tests/assets/tar/safe.tar", "rb").read()), False),
        (io.BytesIO(open("tests/assets/tar/danger.tar", "rb").read()), True),
    ],
)
def test_scan_tar(file_obj, expected):
    result = TokenDetector.scan_tar(file_obj)
    assert result == expected


@pytest.mark.parametrize(
    "file_obj, expected",
    [
        (io.BytesIO(open("tests/assets/zip/safe.zip", "rb").read()), False),
        (io.BytesIO(open("tests/assets/zip/danger.zip", "rb").read()), True),
    ],
)
def test_scan_zip(file_obj, expected):
    result = TokenDetector.scan_zip(file_obj)
    assert result == expected


@pytest.mark.parametrize(
    "ft, buffer, expected",
    [
        ("application/zip", open("tests/assets/zip/safe.zip", "rb").read(), False),
        ("application/zip", open("tests/assets/zip/danger.zip", "rb").read(), True),
        ("application/x-7z-compressed", open("tests/assets/7zip/safe.7z", "rb").read(), False),
        ("application/x-7z-compressed", open("tests/assets/7zip/danger.7z", "rb").read(), True),
        ("application/x-bzip2", open("tests/assets/bzip2/safe.tar.bz2", "rb").read(), False),
        ("application/x-bzip2", open("tests/assets/bzip2/danger.tar.bz2", "rb").read(), True),
        ("application/x-gzip", open("tests/assets/gzip/safe.tar.gz", "rb").read(), False),
        ("application/x-gzip", open("tests/assets/gzip/danger.tar.gz", "rb").read(), True),
        ("application/x-rar", open("tests/assets/rar/safe.rar", "rb").read(), False),
        ("application/x-rar", open("tests/assets/rar/danger.rar", "rb").read(), True),
        ("application/x-tar", open("tests/assets/tar/safe.tar", "rb").read(), False),
        ("application/x-tar", open("tests/assets/tar/danger.tar", "rb").read(), True),
    ],
)
def test_scan_archive(ft, buffer, expected):
    result = TokenDetector.scan_archive(ft, buffer)
    assert result == expected
