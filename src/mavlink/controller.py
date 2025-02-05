from pymavlink import mavutil  # type: ignore
from src.mavlink.error import MavlinkError
from src.mavlink.socket import MavlinkSocket


class MavlinkController(object):
    """
    The Controller class simplifies rover control by eliminating the need to pass lengthy arrays to
    the MAVUtil library.
    """

    def __init__(self, connection: MavlinkSocket):
        """
        Constructor for `Controller`.

        Args:
            connection (Connection): an established connection to send commands over.

        Raises:
            MavCommError: raised if the provided connection is has not been established in advance.
        """

        if not connection.established:
            raise MavlinkError("Provided connection hasn't been established!")

        self._connection = connection
        assert connection.master is not None
        self._master = connection.master

    def arm(self, wait=True) -> None:
        """
        Sends the command to the drone to arm it motors.
        This command is referred to as arming because it allows the rover to prepare its motors for
        action. Similar to arming yourself for combat - I thought this was interesting.

        Args:
            wait (bool, optional): if True wait until the rover has sent a message back informing
                us it's completed arming. Defaults to True.
        """

        params = [1, 0, 0, 0, 0, 0, 0]
        self._send_long_command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                params)
        if wait:
            self._master.motors_armed_wait()

    def disarm(self, wait=True) -> None:
        """
        Sends the command to the drone to disarm it motors.

        Args:
            wait (bool, optional): if True wait until the rover has sent a message back informing
                us it's completed disarming. Defaults to True.
        """

        params = [0, 0, 0, 0, 0, 0, 0]
        self._send_long_command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                params)
        if wait:
            self._master.motors_disarmed_wait()

    def set_mode(self, mode: str) -> None:
        """
        Sets the current flight mode of the rover.
        See `https://ardupilot.org/copter/docs/flight-modes.html` for a list of these modes.

        Todo:
            Add a check that the mode is all caps
            Add a check that the mode is in the mapping
            Check this works for regular modes

        Args:
            mode (str): the flight mode to set for the rover.
        """

        mode_id = self._master.mode_mapping()[mode]
        self._master.mav.set_mode_send(
            self._connection.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )

    def set_position(self, px: float, py: float, pz: float) -> None:
        """
        Sends a command to the rover telling it where to move relative to its current position.
        For example, [0.0, 0.0, 3.0] would tell it to move +3.0 meters upwards from its current
        position.

        Todo:
            Add a check that the position is 3 numbers long

        Args:
            px (float): The position of the goal relative to the agent's current position along the
                x-axis.
            py (float): The position of the goal relative to the agent's current position along the
                y-axis.
            pz (float): The position of the goal relative to the agent's current position along the
                z-axis.
        """

        self._set_position_target_local_ned([px, py, pz])

    def set_velocity(self, vx: float, vy: float, vz: float) -> None:
        """
        Sends a command to the rover telling it how fast to move in the x, y, and z axes in m/s.
        For example, [0.0, -1.0, 2.5] would tell it to move at a rate of +2.5 m/s in the +z
        direction and move 1.0 m/s in the negative y-axis direction.

        Todo:
            Add a check that the velocity is 3 numbers long

        Args:
            vx (float): The velocity for the agent to move along the x-axis.
            vy (float): The velocity for the agent to move along the y-axis.
            vz (float): The velocity for the agent to move along the z-axis.
        """

        self._set_position_target_local_ned([vx, vy, vz], order=1)

    def set_acceleration(self, ax: float, ay: float, az: float) -> None:
        """
        Sends a command to the rover telling it how fast to accelerate in the x, y, and z axes in
        m/s.  For example, [1.2, 0.0, 0.0] would tell it to accelerate at a rate of +1.2 m/s^2 in
        the +x direction.

        Todo:
            Add a check that the acceleration is 3 numbers long

        Args:
            ax (float): The acceleration for the agent along the x-axis.
            ay (float): The acceleration for the agent along the y-axis.
            az (float): The acceleration for the agent along the z-axis.
        """

        self._set_position_target_local_ned([ax, ay, az], order=2)

    def set_yaw(self, yaw, speed, direction=0, relative=True):
        params = [yaw, speed, direction, relative, 0, 0, 0]
        self._send_long_command(
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            params)

    def set_camera_pitch(self, pitch, speed):
        self._send_long_command(
            mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW,
            [pitch, 0, speed, 0, 32, 0, 0]
        )

    def lights(self, on: bool):
        pwm_val = 1500 if on else 0
        params = [10, pwm_val, 0, 0, 0, 0, 0]
        self._send_long_command(
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            params
        )

    def _send_long_command(self, command_id: int, params: list[int] | list[float]) -> None:
        """
        Send a command with seven parameters to the MAV.
        The format for a long command is as follows
        Command_Long = [
            Target System,
            Target Component,
            Command,
            Confirmation,
            Param1,
            Param2,
            Param3,
            Param4,
            Param5,
            Param6,
            Param7
        ]

        Args:
            command_id (int): id of the command to send to the rover.
            params (List[float]): list of params to send to the rover.

        Raises:
            MavCommError: raised if the provided list of parameters isn't of length 7
        """

        if len(params) != 7:
            raise MavlinkError("Long command requires seven parameters!")

        self._master.mav.command_long_send(
            self._connection.target_system,
            self._connection.target_component,
            command_id,
            0,
            *params
        )

    def _set_position_target_local_ned(self, vect: list[float], order=0, coord_frame=9) -> None:
        """
        Sets a desired vehicle position in a local north-east-down coordinate frame.
        Used by an external controller to command the vehicle.

        Todo:
            Check order is in the range [0-2]
            Check the vect is of length 3.

        Args:
            vect (List[float]): A 3 dimensional vector describing either a position,
                velocity, acceleration in the order of [xdim, ydim, zdim].
            order (int, optional): Which type of information to send based on the order of motion.
                0th order is position, 1st order is velocity, and second order is acceleration.
                Defaults to 0.
            coord_frame (int, optional): What coordinate frame should the rover use. Defaults to 9.
        """

        type_mask = [3576, 3527, 3135][order]

        pos = vect if order == 0 else [0] * 3
        vel = vect if order == 1 else [0] * 3
        acc = vect if order == 2 else [0] * 3
        params = pos + vel + acc

        self._master.mav.set_position_target_local_ned_send(
            self._connection.age_of_connection(),
            self._connection.target_system,
            self._connection.target_component,
            coord_frame,
            type_mask,
            *params,
            0,
            0
        )
