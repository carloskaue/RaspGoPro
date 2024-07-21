import asyncio
import json
import logging

from Gopro import GoProWebcamPlayer

#from multi_webcam import GoProWebcamPlayer

logging.getLogger(__name__)

async def main() -> None:
    with open("webcam_config.json") as fp:
        config = json.load(fp)
        for serial, params in config.items():
            print (serial)
            cam = GoProWebcamPlayer(serial, 9000)
            cam.open()
            cam.play(resolution=params["resolution"], fov=params["fov"] )
            input("Press enter to stop")
            cam.close()

if __name__ == "__main__":
    el = asyncio.get_event_loop()
    el.run_until_complete(main())
    el.close
