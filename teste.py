import asyncio
import json
from open_gopro import WiredGoPro
from multi_webcam import GoProWebcamPlayer


PORTS = 9000

# def main(args: argparse.Namespace):
#     webcam1 = GoProWebcamPlayer(args.serial, args.port)
#     webcam1.open()
#     webcam1.play(args.resolution, args.fov)
#     input("Press enter to stop")
#     webcam1.close()


async def main() -> None:
    with open("webcam_config.json") as fp:
        config = json.load(fp)
        for serial, params in config.items():
            print(serial,params['port'] )
            webcam1 = GoProWebcamPlayer(serial, params['port'])
            webcam1.open()
            webcam1.play(params['resolution'], params['fov'])
            input("Press enter to stop")
            webcam1.close()

if __name__ == "__main__":
    #asyncio.run(main())
    el = asyncio.get_event_loop()
    el.run_until_complete(main())
    el.close