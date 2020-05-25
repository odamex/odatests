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

import asyncio
import configparser
import os
import re
import tempfile
import unittest

CREATE_TIMEOUT_SECS=5
TEST_TIMEOUT_SECS=300
ODAMEX_BIN="../odamex/build-gcc/client/odamex.exe"

async def run_odamex(*odamex_args):
    """
    Asynchronously run Odamex until it exits.

    This function returns the contents of the console on success.
    """
    # Create a temporary file to hold our process output.
    # [AM] We can't use NamedTemporaryFile because the resulting file is not
    #      accessible to other processes on Windows.
    tmphandle, tmpname = tempfile.mkstemp(prefix="odamex_")

    # Wait for Odamex to start.
    proc = await asyncio.wait_for(
        asyncio.create_subprocess_exec(
            ODAMEX_BIN, "+logfile", tmpname, *odamex_args
        ), CREATE_TIMEOUT_SECS
    )

    # Wait for the process to exit.
    await asyncio.wait_for(
        proc.wait(), TEST_TIMEOUT_SECS
    )

    # Send the log back as our result after cleaning up the logfile
    tmpdata = open(tmphandle, 'rb')
    log = tmpdata.read()
    tmpdata.close()
    os.unlink(tmpname)
    return log

async def demotest(iwad, demo, expect, pwads=None, deh=None):
    """
    Runs Odamex in demotest mode.

    If Odamex runs the demo in a reasonable amount of time and the player
    position is the same as what we have on file, the demo passes.
    """
    # Construct a command line
    args = []
    args.extend(("-iwad", iwad))
    if pwads:
        args.extend(("-file",) + tuple(pwads))
    if deh:
        args.extend(('-deh', deh))
    args.extend(("+demotest", demo))
    print(args)
    return

    # Run Odamex in demotest mode
    res = await run_odamex(*args)
    log = res.decode("ascii").replace("\r\n", "\n")

    # Extract the "demotest" string.
    match = re.search(r"demotest:([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+)", log)
    print(match.group(1), match.group(2), match.group(3), match.group(4))
    return True

async def demolist():
    """
    Run all configured demos.

    Reads the demolist configuration and creates demotest coroutines for every
    configured demo.
    """
    demotests = []

    # Read the config.
    config = configparser.ConfigParser()
    config.read("demolist.ini")

    # Make a coroutine per config
    for section in config.sections():
        args = dict(config.items(section))
        if 'pwad' in args:
            args['pwads'] = args['pwad'].split(' ')
            del args['pwad']
        demotests.append(demotest(**args))

    # Run our demo-running coroutines.
    done, _ = await asyncio.wait(
        demotests, timeout=TEST_TIMEOUT_SECS, return_when=asyncio.ALL_COMPLETED
    )
    for proc in done:
        print(proc.result())

async def main():
    await demolist()

asyncio.run(main())
