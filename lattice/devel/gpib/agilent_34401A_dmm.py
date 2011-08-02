# Copyright (C) 2007  Matthew Neeley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
### BEGIN NODE INFO
[info]
name = Agilent 34401A DMM
version = 1.1
description = 

[startup]
cmdline = %PYTHON% agilent_34401A_dmm.py
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.gpib import GPIBManagedServer

class AgilentDMMServer(GPIBManagedServer):
    name = 'Agilent 34401A DMM'
    deviceName = 'HEWLETT-PACKARD 34401A'

__server__ = AgilentDMMServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
