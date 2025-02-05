from pymavlink import mavutil  # type: ignore
from typing import Optional
import socket
import time

from src.mavlink.error import MavlinkError


class MavlinkSocket(object):
    """
    The MavlinkSocket class provides a straightforward way to manage MAVLink
    connections, making it easier to communicate with the ROV.
    """

    def __init__(self,
                 hostname: str = '0.0.0.0',
                 port: int = 14550):
        """
        Constructor for MavlinkSocket.

        Args:
            hostname (str, optional): hostname to connect to. Defaults to '0.0.0.0'.
            port (int, optional): port to connect to. Defaults to 14550.
        """

        self.hostname: str = hostname
        self.port: int = port

        # Is the connection actively listening on a port?
        self.listening: bool = False
        # Has the connection recieved a heartbeat?
        self.established: bool = False
        # Time when connection was established?
        self.cnx_start_time: Optional[float] = None
        # Entity representing the serial MAVLink port
        self.master: Optional[mavutil.mavudp] = None

    def listen(self):
        """
        Starts to listen with a UDP protocal at hostname:port.

        Raises:
            MavCommError: raised if the given hostname is invalid.
            MavCommError: raised if the given port is invalid.
        """

        try:
            self.master = mavutil.mavlink_connection(self.cnx_str)
            self.listening = True
        except socket.gaierror:
            raise MavlinkError(f"Provided hostname, {self.hostname}, is invalid.")
        except OverflowError:
            raise MavlinkError(f"Provided port, {self.port} is invalid.")

    def await_heartbeat(self):
        """
        Waits until a heartbeat has been recieved. A heartbeat message in MAVLink
        serves as an acknowledgment of an active connection between the sender and
        receiver, ensuring the communication link is alive and functional.

        Raises:
            MavlinkError: Socket is not currently listening on a port.
        """

        if not self.listening:
            raise MavlinkError("""Must be listening on a port before awaiting a
                               heartbeat.""")
        self.master.wait_heartbeat()
        self.established = True
        self.cnx_start_time = time.time()

    def age_of_connection(self, ms: bool = True) -> int:
        """
        How long has the connection been established?

        Args:
            ms (bool, optional): Return time in milliseconds, otherwise time will be
                returned in seconds. Defaults to True.

        Returns:
            int: how long the connection has been established (age).

        Raises:
            MavCommError: A connection has not been established.
        """

        if self.cnx_start_time is None:
            raise MavlinkError("""Connection needs to be established prior to querying
                               its age.""")

        return int((time.time() - self.cnx_start_time) * (1000 if ms else 1))

    @property
    def target_system(self) -> Optional[int]:
        """
        System ID of the connected system.
        """

        if self.established:
            assert self.master is not None
            return self.master.target_system
        else:
            return None

    @property
    def target_component(self) -> Optional[int]:
        """
        Target component in the connected system.
        """

        if self.established:
            assert self.master is not None
            return self.master.target_component
        else:
            return None

    @property
    def cnx_str(self) -> str:
        """
        Representation of the connection as a string.

        Returns:
            str: representation of the connection as a string.
        """

        return f"udp:{self.hostname}:{self.port}"
