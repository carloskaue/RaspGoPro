import asyncio
import json
import logging
import threading

from Gopro import GoProWebcamPlayer

#webcam_config.json
#serial = "xxx"  the last 3 numbers
#resolution = "720p" or "1080p"
#fov =  "LINEAR", "NARROW", "SUPERVIEW" or "WIDE"
    
def OpenCam(cam):
    cam.open()
    cam.play()

def CloseCam(cam):
    cam.close
    
async def main() -> None:
    with open("webcam_config.json") as fp:
        config = json.load(fp)
        camList = []

        print(f'Resolution: {config["resolution"]}')
        print(f'FOV: {config["fov"]}')

        for serial, param in config["cam"].items():
            print (f'\tSerial: {serial}\tPort: {param["port"]}')
            
            camList.append((GoProWebcamPlayer(  serial     = serial, 
                                                port       = param["port"],
                                                resolution = config["resolution"],
                                                fov        = config["fov"])))

        threads = [threading.Thread(target=OpenCam, args=(cam,)) for cam in camList]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        input("Press enter to stop")
        [CloseCam(cam) for cam in camList ]


if __name__ == "__main__":
    el = asyncio.get_event_loop()
    el.run_until_complete(main())
    el.close
