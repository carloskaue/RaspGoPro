from __future__ import annotations
import json
import enum
import logging
import itertools
import multiprocessing as mp
from typing import Any, Protocol, Optional
import cv2 as cv
import requests

logging.getLogger(__name__)

REDUCTION = 25/100


class SupportsWebcam(Protocol):
    def release(self) -> None:
        ...

    def read(self) -> None:
        ...

class Player:
    """The Webcam Stream Viewer via Open CV

    Note that each player runs in a separate process.
    """

    def __init__(self) -> None:
        """Constructor"""
        self._vid: SupportsWebcam
        self._process = mp.Process(target=self._run, daemon=True)
        self._player_started = mp.Event()
        self._stop_player = mp.Event()
        self._url: str
    
    @property
    def is_running(self) -> bool:
        """Is the player currently running?

        Returns:
            bool: True if yes, False if no
        """
        return self._player_started.is_set()
    
    @property
    def url(self) -> str:
        """The URL that is being used to view the stream (minus any OpenCV args)

        Returns:
            str: stream URL
        """
        return self._url
    
    @url.setter
    def url(self, url: str) -> None:
        if self.is_running:
            raise RuntimeError("Can not set URL while player is running")
        self._url = url
    
    def _run(self) -> None:
        """The main stream display loop.

        While the player is running, get a frame and display it
        """
        self._vid = cv.VideoCapture(self.url + "?overrun_nonfatal=1&fifo_size=50000000", cv.CAP_FFMPEG)
        self._player_started.set()
        logging.info("Player started.")
        cv.namedWindow("frame", cv.WINDOW_NORMAL)
        while not self._stop_player.is_set():
            ret, frame = self._vid.read()
            if ret:
                height, width = frame.shape[:2]
                height = int(height*REDUCTION)
                width = int(width*REDUCTION)
                imag = cv.resize(frame, (width, height))  
                cv.imshow("frame", imag)

           # cv.waitKey(1)  # Show for 1 millisecond
        # After the loop release the cap object
        self._vid.release()
        # Destroy all the windows
        cv.destroyAllWindows()


    def start(self, url: str) -> None:
        """Start the stream player

        Args:
            url (str): URL to view stream at
        """
        logging.info(f"Starting player @ {url}")
        self.url = url
        self._process.start()
        self._player_started.wait()

    def stop(self) -> None:
        """Stop the stream player and wait for the process to stop"""
        if self.is_running:
            logging.info("Stopping player")
            self._stop_player.set()
            self._process.join()