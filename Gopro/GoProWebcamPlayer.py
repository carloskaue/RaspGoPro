from __future__ import annotations
import logging
import itertools
import multiprocessing as mp
from typing import Any,  Optional

from .Webcam import Webcam
from .Player import Player

logging.getLogger(__name__)

class GoProWebcamPlayer:
    """Configure and view a GoPro webcam stream

    This is the top level class that will both configure the GoPro via HTTP and start the Open CV stream
    to display frames received from the GoPro.

    It also manages the ports used across multiple GoPros to ensure there are no overlaps.
    """

    STREAM_URL = "udp://0.0.0.0:{port}"
    _used_ports: set[int] = set()
    _free_port: itertools.count[int] = itertools.count(start=8554)

    @classmethod
    def _get_free_port(cls) -> int:
        """Find a port that is not currently being used.

        Returns:
            int: available port
        """
        while (port := next(cls._free_port)) in cls._used_ports:
            continue
        return port
    
    def __init__(self, serial: str, port: Optional[int] = None) -> None:
        """Constructor

        Args:
            serial (str): (at least) last 3 digits of GoPro's serial number
            port (Optional[int], optional): Port that GoPro will stream to. Defaults to
                None (will be auto-assigned starting at 8554).

        Raises:
            RuntimeError: The desired port is already used.
        """
        self.serial = serial
        self.webcam = Webcam(serial)
        self.player = Player()
        if port and port in GoProWebcamPlayer._used_ports:
            raise RuntimeError(f"Port {port} is already being used")
        self.port = port or GoProWebcamPlayer._get_free_port()
        GoProWebcamPlayer._used_ports.add(self.port)
        logging.debug(f"Using port {self.port}")
    
    def __enter__(self) -> GoProWebcamPlayer:
        self.open()
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def open(self) -> None:
        """Enable the GoPro webcam."""
        self.webcam.enable()

    def play(self, resolution: Optional[int] = None, fov: Optional[int] = None) -> None:
        """Configure and start the GoPro Webcam. Then open and display the stream.

        Note that the FOV and Resolution param values come from the Open GoPro Spec:
        https://gopro.github.io/OpenGoPro/http#tag/settings

        Args:
            resolution (Optional[int]): Resolution for webcam stream. Defaults to None (will be assigned by GoPro).
            fov (Optional[int]): Field of view for webcam stream. Defaults to None (will be assigned by GoPro).
        """
        self.webcam.start(self.port, resolution, fov)
        self.player.start(GoProWebcamPlayer.STREAM_URL.format(port=self.port))

    def close(self) -> None:
        """Stop the stream player and disable the GoPro webcam"""
        self.player.stop()
        self.webcam.disable()