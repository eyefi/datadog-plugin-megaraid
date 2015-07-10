#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict

from checks import AgentCheck

class megaraid(AgentCheck):
    def check(self, instance):
        currentAdapterNumber = -1
        currentPhysicalDriveNumber = -1
        totalMediaErrorCount = 0
        maximumMediaErrorCount = 0
        totalOtherErrorCount = 0
        maximumOtherErrorCount = 0
        failedPhysicalDrives = { }
        currentVirtualDriveNumber = -1
        virtualDrivesByState = defaultdict(lambda: 0)
        virtualDrivesByState['optimal'] = 0
        virtualDrivesByState['degraded'] = 0
        virtualDrivesByState['unknown'] = 0
        parsedCurrentVirtualDriveState = False

        # Run the MegaRAID command to query all physical drives
        with os.popen('sudo /opt/MegaRAID/MegaCli/MegaCli64 -LdPdInfo -aALL', 'r') as pipe:
            for line in pipe:
                # If the line is the beginning of a new adapter section...
                match = re.search(r'^Adapter #(\d+)', line)
                if match:
                    currentAdapterNumber = int(match.group(1))
                    continue

                # If the line is the beginning of a new physical drive section...
                if re.search(r'^PD:\s+\d+\s+Information', line):
                    currentPhysicalDriveNumber += 1
                    continue

                # If the line has the number of media errors for the current physical drive...
                match = re.search(r'^Media\s+Error\s+Count:\s+(\d+)', line)
                if match:
                    count = int(match.group(1))
                    if count > 0:
                        failedPhysicalDrives[currentPhysicalDriveNumber] = 1
                        totalMediaErrorCount += count
                        if count > maximumMediaErrorCount:
                            maximumMediaErrorCount = count
                    continue

                # If the line has the number of other errors for the current physical drive...
                match = re.search(r'^Other\s+Error\s+Count:\s+(\d+)', line)
                if match:
                    count = int(match.group(1))
                    if count > 0:
                        failedPhysicalDrives[currentPhysicalDriveNumber] = 1
                        totalOtherErrorCount += count
                        if count > maximumOtherErrorCount:
                            maximumOtherErrorCount = count
                    continue

        # Run the MegaRAID command to query all virtual drives (i.e. arrays)
        with os.popen('sudo /opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -Lall -aALL', 'r') as pipe:
            for line in pipe:
                # If the line is the beginning of a new virtual drive section...
                match = re.search(r'^Virtual\s+Drive:\s+(\d+)', line)
                if match:
                    if currentVirtualDriveNumber >= 0 and not parsedCurrentVirtualDriveState:
                        virtualDrivesByState['unknown'] += 1
                    currentVirtualDriveNumber += 1
                    parsedCurrentVirtualDriveState = False
                    continue

                # If the line has the state of the current virtual drive...
                match = re.search(r'^State\s+:\s+(\S+)', line)
                if match:
                    state = match.group(1).lower()
                    virtualDrivesByState[state] += 1
                    parsedCurrentVirtualDriveState = True
                    continue

        # If the state of the last virtual drive was not parsed...
        if currentVirtualDriveNumber >= 0 and not parsedCurrentVirtualDriveState:
            virtualDrivesByState['unknown'] += 1

        # Send metrics
        self.gauge('megaraid.drives.total', currentPhysicalDriveNumber+1)
        self.gauge('megaraid.drives.failed', len(failedPhysicalDrives.keys()))
        self.gauge('megaraid.errors.media.total', totalMediaErrorCount)
        self.gauge('megaraid.errors.media.maximum', maximumMediaErrorCount)
        self.gauge('megaraid.errors.other.total', totalOtherErrorCount)
        self.gauge('megaraid.errors.other.maximum', maximumOtherErrorCount)
        self.gauge('megaraid.arrays.total', currentVirtualDriveNumber+1)
        for state in virtualDrivesByState:
            self.gauge('megaraid.arrays.' + state, virtualDrivesByState[state])
