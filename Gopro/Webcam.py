from __future__ import annotations
import json
import enum
import logging
import multiprocessing as mp
from typing import Any, Optional

import cv2 as cv
import requests

logging.getLogger(__name__)

class Webcam:
    BASE_IP = "172.2{}.1{}{}.51"
    BASE_ENDPOINT = "http://{ip}:8080/gopro/"

    class WebcamResolution(enum.Enum):
        RES_1080P = 12
        RES_720p = 7

    class WebcamFOV(enumerate):
        LINEAR    = 4
        NARROW    = 2
        SUPERVIEW = 3
        WIDE      = 0
    
    class Endpoint(enum.Enum):
        WIRELESS_USB_DISABLE = "camera/control/wired_usb?p=0"
        GET_DATE_TIME = "camera/get_date_time"
        GET_WEBCAM_STATUS = "webcam/status"
        START_PREVIEW = "webcam/preview"
        START_WEBCAM = "webcam/start"
        STOP_WEBCAM = "webcam/stop"
        DISABLE_WEBCAM = "webcam/exit"

    class State(enum.IntEnum):
        DISABLED = enum.auto()
        READY = enum.auto()
        LOW_POWER_PREVIEW = enum.auto()
        HIGH_POWER_PREVIEW = enum.auto()
    
    def __init__(self, serial: str) -> None:
        """Constructor

        Args:
            serial (str): (At least) last 3 digits of GoPro's serial number
        """
        self.ip = self.BASE_IP.format(*serial[-3:])
        self.state = self.State.DISABLED
        self._base_url = self.BASE_ENDPOINT.format(ip=self.ip)

    def _send_http_no_validate(self, endpoint: Webcam.Endpoint, **kwargs) -> requests.Response:
        logging.debug(f"Sending {endpoint.value}: {kwargs}")
        response = requests.get(self._base_url + endpoint.value, params=kwargs)
        logging.debug(f"HTTP return code {response.status_code}")
        logging.debug(json.dumps(response.json(), indent=4))
        return response
    
    def _send_http(self, endpoint: Webcam.Endpoint, **kwargs) -> requests.Response:
        response = self._send_http_no_validate(endpoint, **kwargs)
        response.raise_for_status()
        return response
    
    def enable(self) -> None:
        """Prepare the GoPro to be ready to function as a webcam"""
        self._send_http_no_validate(self.Endpoint.WIRELESS_USB_DISABLE)
        self.state = self.State.READY

    def preview(self) -> None:
        """Start the webcam preview"""
        logging.info("Starting preview")
        self._send_http(self.Endpoint.START_PREVIEW)
        self.state = self.State.LOW_POWER_PREVIEW
    
    def start(self, port: Optional[int] = None, resolution: Optional[int] = WebcamResolution.RES_720p, fov: Optional[int] = WebcamFOV.LINEAR ) -> None:
        """Start the webcam stream

        Note that the FOV and Resolution param values come from the Open GoPro Spec:
        https://gopro.github.io/OpenGoPro/http#tag/settings

        Args:
            port (Optional[int]): Port to stream to. Defaults to None (will be auto-assigned by the camera).
            resolution (Optional[int]): Resolution to use. Defaults to None (will be auto-assigned by the camera).
            fov (Optional[int]): Field of View to use. Defaults to None (will be auto-assigned by the camera).
        """
        logging.info("Starting webcam")
        params = {}
        for setting, key in zip([port, resolution, fov], ["port", "res", "fov"]):
            if setting is not None:
                params[key] = setting
        self._send_http(self.Endpoint.START_WEBCAM, **params)
        self.state = self.State.HIGH_POWER_PREVIEW
        logging.info("Webcam started successfully")

    def stop(self) -> None:
        """Stop the webcam stream"""
        logging.info("Stopping webcam")
        self._send_http(self.Endpoint.STOP_WEBCAM)
        self.state = self.State.READY

    def disable(self) -> None:
        """Disable the webcam"""
        logging.info("Disabling webcam")
        self._send_http(self.Endpoint.DISABLE_WEBCAM)
        self.state = self.State.DISABLED