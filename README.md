# OdaTests

This test system runs a series of vanilla demos to check Odamex's vanilla compatibility. It consists of 3 parts:

## Wads Directory
The Wads directory contains all the wads needed to run demo tests. You might inquire about IWADs.
Each release of the resource files have encrypted IWADs with the password kept in a password safe.
To run your own tests, you'll need your own IWADs.

## Demos Directory
This directory contains all the demos that will be run by the tester.
Currently, only vanilla DOOM demos are supported.

## demolist.ini
Here's the main configuration file for the demo tester. This file will list all demos that will be tested. Check the
`demolist.ini.example` file for more information.

## Example Resource Repo
Check the repo [Odamex-Resources](https://github.com/bcahue/odatests-resources) to see an example of how resource repos should
be laid out for inclusion in an Odamex build pipeline.