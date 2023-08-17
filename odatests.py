#!/usr/bin/env python3

#  $Id: $
#
#  Copyright (C) 2000-2006 by Sergey Makovkin (CSDoom .62)
#  Copyright (C) 2006-2022 by The Odamex Team.
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

from pathlib import Path
from typing import Any, Dict, List, Optional

if not os.getenv('CREATE_TIMEOUT_SECS'):
    CREATE_TIMEOUT_SECS = 5
else:
    CREATE_TIMEOUT_SECS = int(os.getenv('CREATE_TIMEOUT_SECS'))

if not os.getenv('TEST_TIMEOUT_SECS'):
    TEST_TIMEOUT_SECS = 300
else:
    TEST_TIMEOUT_SECS = int(os.getenv('TEST_TIMEOUT_SECS'))

if not os.getenv('ODAMEX_BIN'):
    ODAMEX_BIN = r"C:\Users\Blair\source\repos\odamex-alt\out\build\x64-Debug\client\odamex.exe"
else:
    ODAMEX_BIN = os.getenv('ODAMEX_BIN')

if not os.getenv('MAX_ODAMEX_PROCS'):
    MAX_ODAMEX_PROCS = 4
else:
    MAX_ODAMEX_PROCS = int(os.getenv('MAX_ODAMEX_PROCS'))

class DemoTest ():
    def resolve_demo(demo: str) -> str:
        """
        Resolve a demo file or lump to something we can pass to Odamex.
        """
        p = Path("demos") / demo
        if not p.exists():
            # This demo does not exist, must be a lump.
            return demo

        # This file exists, return it.
        return ".\\" +str(p)


    def resolve_wad(wad: str) -> str:
        """
        Resolve a demo file or lump to something we can pass to Odamex.
        """
        p = Path("wads") / wad
        if not p.exists():
            ex = "WAD does not exist: {}".format(wad)
            raise RuntimeError(ex)

        # This file exists, return it.
        return str(p)

    def resolve_wads(wads: List[str]) -> tuple:
        """
        Resolve a list of pwads, and print if the file can't be found.
        """
        wadlist = []
        for w in wads:
            p = Path("wads") / w

            if not p.exists():
                 ex = "WAD does not exist: {}".format(w)
                 raise RuntimeError(ex)
            else:
                wadpath = str(p)

            wadlist.append(wadpath)

        # All files exists, return them.
        return tuple(wadlist)


    async def run_odamex(*odamex_args: str) -> bytes:
        """
        Asynchronously run Odamex until it exits.

        This function returns the contents of the console on success.
        """
        print("RUN: ", *odamex_args)

        # Create a temporary file to hold our process output.
        # [AM] We can't use NamedTemporaryFile because the resulting file is not
        #      accessible to other processes on Windows.
        tmphandle, tmpname = tempfile.mkstemp(prefix="odamex_")

        odargs = (ODAMEX_BIN, *odamex_args, "+logfile", tmpname)

        oargs = " ".join(odargs)

        # Wait for Odamex to start.
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_shell(oargs,
                                            stdout=asyncio.subprocess.PIPE,
                                            stderr=asyncio.subprocess.PIPE),
            CREATE_TIMEOUT_SECS,
        )

        # Wait for the process to exit.
        await asyncio.wait_for(proc.wait(), TEST_TIMEOUT_SECS)

        # Send the log back as our result after cleaning up the logfile
        tmpdata = open(tmphandle, "rb")
        log = tmpdata.read()
        tmpdata.close()
        os.unlink(tmpname)
        return log


    async def demotest(
        procs: asyncio.Semaphore,
        section: str,
        iwad: str,
        demo: str,
        expect: str,
        pwads: Optional[List[str]] = None,
        deh: Optional[str] = None,
    ) -> tuple:
        """
        Runs Odamex in demotest mode.

        If Odamex runs the demo in a reasonable amount of time and the player
        position is the same as what we have on file, the demo passes.
        """
        async with procs:
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)

            # Construct a command line
            args: List[str] = []
            args.extend(("-iwad", DemoTest.resolve_wad(iwad)))
            if pwads:
                args.extend(("-file",) + DemoTest.resolve_wads(pwads))
            if deh:
                args.extend(("-deh", deh))
            args.extend(("+demotest", DemoTest.resolve_demo(demo)))

            # Run Odamex in demotest mode
            res = await DemoTest.run_odamex(*args)
            log = res.decode("ascii", "ignore").replace("\r\n", "\n")

            # Extract the "demotest" string.
            match = re.search(
                r"demotest:([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+)", log
            )
            if match is None:
                print(*args, "No Match")
                return section, False

            # Check if expect == actual
            actual = " ".join(match.groups())
            if expect != actual:
                print(*args, expect, actual, "expect != actual")
                return section, False

            print(*args, "PASS")
            return section, True


    async def demolist() -> list:
        """
        Run all configured demos.

        Reads the demolist configuration and creates demotest coroutines for every
        configured demo.
        """
        demotests = []
        procs = asyncio.Semaphore(MAX_ODAMEX_PROCS)

        # Read the config.
        config = configparser.ConfigParser()
        config.read("demolist.ini")

        # Make a coroutine per config
        for section in config.sections():
            args: Dict[str, Any] = dict(config.items(section))
            if "pwad" in args:
                args["pwads"] = args["pwad"].split(" ")
                del args["pwad"]
            demotests.append(DemoTest.demotest(procs, section, **args))

        # Run our demo-running coroutines.
        done, _ = await asyncio.wait(
            demotests, timeout=TEST_TIMEOUT_SECS, return_when=asyncio.ALL_COMPLETED
        )
        results = []

        for proc in done:
                results.append(proc.result())

        return results



#async def main() -> None:
#    await DemoTest.demolist()


#asyncio.run(main())
