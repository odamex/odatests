#!/usr/bin/env python3

#  $Id: $
#
#  Copyright (C) 2000-2006 by Sergey Makovkin (CSDoom .62)
#  Copyright (C) 2006-2020 by The Odamex Team.
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

from base64 import b64encode, b64decode
from pathlib import Path
import nacl.secret
import nacl.utils
import os
import sys


def rot13(instr: str) -> str:
    """
    Apply ROT13 to string.

    This is just a simple strategy to prevent these sought-after wads from
    showing up in Google searches for these WAD's.  Not that it would do
    them any good, since they're encrypted.
    """
    outstr = ""
    for ch in instr:
        if ch >= "A" and ch <= "Z":
            index = ord(ch) - ord("A")
            index = (index + 13) % 26
            outstr += chr(index + ord("a"))
        elif ch >= "a" and ch <= "z":
            index = ord(ch) - ord("a")
            index = (index + 13) % 26
            outstr += chr(index + ord("a"))
        else:
            outstr += ch
    return outstr


def encrypt(wad: str, key: bytes) -> None:
    """
    Encrypt a file.
    """
    src = Path("wads") / (wad + ".wad")
    dst = Path("wads") / (rot13(wad) + ".wad.bin")

    plaintext = src.read_bytes()
    box = nacl.secret.SecretBox(key)
    ciphertext = box.encrypt(plaintext)
    dst.write_bytes(ciphertext)


def decrypt(wad: str, key: bytes) -> None:
    """
    Decrypt a file.
    """
    src = Path("wads") / (rot13(wad) + ".wad.bin")
    dst = Path("wads") / (wad + ".wad")

    ciphertext = src.read_bytes()
    box = nacl.secret.SecretBox(key)
    plaintext = box.decrypt(ciphertext)
    dst.write_bytes(plaintext)


def genkey() -> None:
    """
    Generate a secret key.
    """
    SECRET_KEY = b64encode(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)).decode(
        "ascii"
    )
    print(f"SECRET_KEY={SECRET_KEY}")


def print_help() -> None:
    print("secret.py - Encrypts and decrypts WAD files stored in the repository")
    print("")
    print("An environment variable named SECRET_KEY must be set, containing a 32 byte")
    print("(64 hex character) key.")
    print("")
    print("Usage:")
    print("  > secret.py encrypt <WADNAME>")
    print("  Encrypts a WAD file.")
    print("")
    print("  > secret.py decrypt <WADNAME>")
    print("  Decrypts a WAD file.")
    print("")
    print("WADNAME parameter must be all-lowercase with no directory or extension.")
    print("When decrypting, use the original WAD name, not the scrambled one.")
    sys.exit(1)


if __name__ == "__main__":
    subs = {"encrypt", "decrypt", "genkey"}

    if not sys.argv[1] in subs:
        print("Unknown sub-command")
        print_help()
        sys.exit(1)

    sub = sys.argv[1]
    if sub == "genkey":
        genkey()
    else:
        if not "SECRET_KEY" in os.environ:
            print("Environment variable SECRET_KEY is missing")
            print_help()
            sys.exit(1)

        if len(sys.argv) < 3:
            print("Not enough parameters")
            print_help()
            sys.exit(1)

        SECRET_KEY = os.environ["SECRET_KEY"]
        if sub == "encrypt":
            encrypt(sys.argv[2], b64decode(SECRET_KEY))
        elif sub == "decrypt":
            decrypt(sys.argv[2], b64decode(SECRET_KEY))
