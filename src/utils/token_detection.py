"""
This module contains the functions for token detection.
"""

import binascii
import bz2
import gzip
import io
import re
import tarfile
import zipfile
from base64 import b64decode

import discord
import magic
import py7zr
import rarfile


class TokenDetector:
    """
    The class for token detection.
    """

    TOKEN_REGEX = re.compile(r"[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27,}")
    MIME = magic.Magic(mime=True)

    def validate(token: str) -> bool:
        """
        Validate the token.

        :param token: The token to validate.
        :type token: str

        :return: Whether the token is valid.
        :rtype: bool
        """
        try:
            decoded = b64decode(token.split(".")[0] + "==")
        except binascii.Error:
            return False
        else:
            return decoded.isdigit()

    @classmethod
    def detect(cls, content: str) -> bool:
        """
        Determine whether the content contains a token.

        :param content: The content to detect.
        :type content: str

        :return: Whether the token is detected.
        :rtype: bool
        """
        possible_tokens = cls.TOKEN_REGEX.findall(content)
        return any(cls.validate(token) for token in possible_tokens)

    @classmethod
    def decoder_search(cls, data: bytes) -> bool:
        """
        Search for tokens in the encoded data.

        :param data: The encoded data to search.
        :type data: bytes

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            return False
        else:
            return cls.detect(content)

    @classmethod
    def scan_zip(cls, file_obj: io.BytesIO) -> bool:
        """
        Scan the zip archive for tokens.

        :param file_obj: The zip archive to scan.
        :type file_obj: io.BytesIO

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            zf = zipfile.ZipFile(file_obj)
        except Exception:
            return False
        else:
            files = zf.namelist()
            files = files if len(files) <= 25 else files[:25]
            return any(cls.decoder_search(zf.read(i)) for i in files)

    @classmethod
    def scan_7z(cls, file_obj: io.BytesIO) -> bool:
        """
        Scan the 7z archive for tokens.

        :param file_obj: The 7z archive to scan.
        :type file_obj: io.BytesIO

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            zf = py7zr.SevenZipFile(file_obj)
        except Exception:
            return
        else:
            files = zf.getnames()
            files = files if len(files) <= 25 else files[:25]
            return any(cls.decoder_search(zf.read(i)[i].read()) for i in files)

    @classmethod
    def scan_rar(cls, file_obj: io.BytesIO) -> bool:
        """
        Scan the rar archive for tokens.

        :param file_obj: The rar archive to scan.
        :type file_obj: io.BytesIO

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            zf = rarfile.RarFile(file_obj)
        except Exception:
            return False
        else:
            files = zf.namelist()
            files = files if len(files) <= 25 else files[:25]
            return any(cls.decoder_search(zf.read(i)) for i in files)

    @classmethod
    def scan_tar(cls, file_obj: io.BytesIO) -> bool:
        """
        Scan the tar archive for tokens.

        :param file_obj: The tar archive to scan.
        :type file_obj: io.BytesIO

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            file_obj.seek(0)
            zf = tarfile.open(fileobj=file_obj)
        except Exception:
            return False
        else:
            files = zf.getmembers()
            files = files if len(files) <= 25 else files[:25]
            return any(cls.decoder_search(zf.extractfile(i).read()) for i in files)

    @classmethod
    def scan_gzip(cls, file_obj: io.BytesIO) -> bool:
        """
        Scan the gzip archive for tokens.

        :param file_obj: The gzip archive to scan.
        :type file_obj: io.BytesIO

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            buf = gzip.decompress(file_obj.read())
        except Exception:
            return False
        else:
            zf = io.BytesIO(buf)
            return cls.scan_tar(zf) if tarfile.is_tarfile(zf) else cls.decoder_search(buf)

    @classmethod
    def scan_bz2(cls, file_obj: io.BytesIO) -> bool:
        """
        Scan the bz2 archive for tokens.

        :param file_obj: The bz2 archive to scan.
        :type file_obj: io.BytesIO

        :return: Whether the token is detected.
        :rtype: bool
        """
        try:
            buf = bz2.decompress(file_obj.read())
        except Exception:
            return False
        else:
            zf = io.BytesIO(buf)
            return cls.scan_tar(zf) if tarfile.is_tarfile(zf) else cls.decoder_search(buf)

    @classmethod
    def scan_archive(cls, ft: str, buffer: bytes) -> bool:
        """
        Scan the archive for tokens.

        :param ft: The MIME type of the archive.
        :type ft: str
        :param buffer: The archive to scan.
        :type buffer: bytes

        :return: Whether the token is detected.
        :rtype: bool
        """
        file_obj = io.BytesIO(buffer)
        if ft.endswith("/zip"):
            return cls.scan_zip(file_obj)
        elif ft.endswith("/x-7z-compressed"):
            return cls.scan_7z(file_obj)
        elif ft.endswith("/x-rar"):
            return cls.scan_rar(file_obj)
        elif ft.endswith("/x-tar"):
            return cls.scan_tar(file_obj)
        elif ft.endswith("/gzip") or ft.endswith("/x-gzip"):
            return cls.scan_gzip(file_obj)
        elif ft.endswith("x-bzip2"):
            return cls.scan_bz2(file_obj)
        return False

    @classmethod
    async def scan_attachment(
        cls, attachment: discord.Attachment, check_textfile: bool, check_archive: bool
    ) -> bool:
        """
        Scan the attachment for tokens.

        :param attachment: The attachment to scan.
        :type attachment: discord.Attachment
        :param check_textfile: Whether to check text files.
        :type check_textfile: bool
        :param check_archive: Whether to check archives.
        :type check_archive: bool

        :return: Whether the token is detected.
        :rtype: bool
        """
        if attachment.size > 25 * 1024 * 1024:
            return False
        buffer = await attachment.read()
        ft = cls.MIME.from_buffer(buffer)
        if not check_textfile:
            return False

        if ft.startswith("text"):
            return cls.decoder_search(buffer)
        elif check_archive and ft.startswith("application"):
            return cls.scan_archive(ft, buffer)
        return False
