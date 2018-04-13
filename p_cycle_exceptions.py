class PCycleException(Exception):
    r"""Base class for other exceptions raised on a PDU power-cycle."""
    pass


class InvalidOutletNumberException(PCycleException):
    r"""Raised if we have a invalid outlet number."""

    def __init__(self, outlet_number, outlet_count):
        self.outlet_number = outlet_number
        self.outlet_count = outlet_count

    def __str__(self):
        return("Invalid outlet number {}. Valid outlet range is (1,{}), both inclusive.".format(self.outlet_number, self.outlet_count))


class PowerOffTimeoutException(PCycleException):
    r"""Raised when a 'PowerOff' reaches its timeout value."""

    def __init__(self, outlet_number):
        self.outlet_number = outlet_number

    def __str__(self):
        return("Timeout reached on waiting for 'Power off' on outlet {}. Please re-try.".format(self.outlet_number))


class PowerOnTimeoutException(PCycleException):
    r"""Raised when a 'PowerOn' reaches its timeout value."""

    def __init__(self, outlet_number):
        self.outlet_number = outlet_number

    def __str__(self):
        return("Timeout reached on waiting for 'Power on' on outlet {}. Please re-try.".format(self.outlet_number))


class PowerOffPingException(PCycleException):
    r"""Raised when a 'PowerOff' fails."""

    def __str__(self):
        return("System pingable after power off. ePDU is having issues and needs someone to power cycle it or there is a configuration change that was made and someone needs to verify the system is connected to the relays / outlets. Please contact lab support team.")


class PowerOnPingException(PCycleException):
    r"""Raised when a 'PowerOn' fails."""

    def __str__(self):
        return("System not reachable after Power cycle. ePDU is having issues and needs someone to power cycle it or there is a configuration change that was made and someone needs to verify the system is connected to the relays / outlets. Please contact lab support team.")
