#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2016 Ivor Wanders
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from . import protocol
from .interact import Communicator
import argparse
import time
import sys

from collections import namedtuple
Cmd = namedtuple("Cmd", ["request", "help"])


parser = argparse.ArgumentParser(description="GPS Pod: Interact with ")
parser.add_argument('--verbose', '-v', help="Print all communication.",
                    action="store_true", default=False)

subparsers = parser.add_subparsers(dest="command")


single_commands = {
    "device":Cmd(protocol.DeviceInfoRequest, "Request device info"),
    "reset":Cmd(protocol.SendResetRequest, "Reset"),
    "settings":Cmd(protocol.ReadSettingsRequest, "Request settings"),
    "status":Cmd(protocol.DeviceStatusRequest, "Request device status"),
    "logcount":Cmd(protocol.LogCountRequest, "Request log count"),
    "logrewind":Cmd(protocol.LogHeaderRewindRequest, "Request header unwind"),
    "logpeek":Cmd(protocol.LogHeaderPeekRequest, "Request header peek"),
    "logstep":Cmd(protocol.LogHeaderStepRequest, "Request header step"),
    "logformat":Cmd(protocol.LogHeaderFormatRequest, "Request log format"),
}

for command in single_commands:
    spec = single_commands[command]
    sub_parser = subparsers.add_parser(command, help=spec.help)

dump_rom = subparsers.add_parser("dump", help="Make a dump of some memory")
dump_rom.add_argument('-upto', type=int, default=int(0x3c0000 / 0x0200),
                      help='number of blocks to retrieve')
dump_rom.add_argument('--file', type=str, default="/tmp/dump.bin",
                      help='file to write to')

# parse the arguments.
args = parser.parse_args()

# no command
if (args.command is None):
    parser.print_help()
    parser.exit()
    sys.exit(1)

# single command.
if (args.command in single_commands):
    spec = single_commands[args.command]
    c = Communicator()
    c.connect()
    req = spec.request()
    c.write_msg(req)
    print("{:s}".format(c.read_msg()))

if (args.command == "dump"):
    up_to_block = max(min(int(0x3c0000 / 0x0200), int(args.upto)), 0)
    print("Up to {:>04X} (decimal: {:>04d}).".format(up_to_block, up_to_block))
    c = Communicator()
    c.connect()
    p = protocol.DataRequest()
    f = open(args.file, "bw")
    sequence_number = 0
    for i in range(up_to_block):
        p.pos(i * p.block_size)
        c.write_msg(p)
        ret_packet = c.read_msg()
        print("{:s}".format(ret_packet))
        f.write(ret_packet.content())
        time.sleep(0.01)
        sequence_number += 1
        
    f.close()