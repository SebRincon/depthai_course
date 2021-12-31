import depthai as dai
import numpy as np
import cv2

#    ┌──────OAK D───────────┐
# ┌──┴──────┐           ┌───┴────┐          ┌────┐
# │Left Mono│◀──────────│XLinkIn │ ───┬────▶│Host│
# │ Camera  ├────┐      └───┬────┘    │     └────┘
# └──┬──────┘    │      ┌───┴────┐    │
#    │           └─────▶│XLinkOut│────│───────┐
#    │                  └───┬────┘    │       │
# ┌──┴────────┐         ┌───┴────┐    │       │
# │Right Mono │◀────────│XLinkIn │────┘       │
# │  Camera   ├───┐     └───┬────┘            │
# └──┬────────┘   │     ┌───┴────┐            │
#    │            └────▶│XLinkOut│───────────┐│
#    │                  └───┬────┘           ││
#    └──────────────────────┘                ││
#    ┌───────────┐            ┌───────────┐  ││
# ┌──│Right Frame│◀─getFrame──│Right Queue│◀─┘│
# │  └───────────┘            └───────────┘   │
# │  ┌───────────┐            ┌───────────┐   │
# ├──│Left Frame │◀─getFrame──│Left Queue │◀──┘
# │  └───────────┘            └───────────┘
# │  ┌─────────────────────────────────────┐
# └─▶│np.uint8(leftFrame/2 + rightFrame/2) │──┐
#    └─────────────────────────────────────┘  │
#              ┌───────────────────────────┐  │
#              │cv2.imshow("Window", imOut)│◀─┘
#              └───────────────────────────┘


def getFrame(queue):
    frame = queue.get()
    return frame.getCvFrame()


def getStereoPair(pipeline, monoLeft, monoRight):
    stereo = pipeline.createStereoDepth()
    # Checks for ocluded pixels and checks them as valid
    stereo.setLeftRightCheck(True)

    # configure left and right cameras to work as stereo pair
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    return stereo


def mouseCallback(event, x, y, flags, param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseY = y
        mouseX = x


def getMonoCamera(pipeline, side: str):
    # Creating mono camera node and setting the resolution
    mono = pipeline.createMonoCamera()
    mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    # Setting the side
    if side.lower() == 'right':
        mono.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    else:
        mono.setBoardSocket(dai.CameraBoardSocket.LEFT)

    return mono


if __name__ == "__main__":
    mouseX = 0
    mouseY = 640

    # Defineing the pipeline
    pipeline = dai.Pipeline()

    # Defining the monoCameras
    monoLeft = getMonoCamera(pipeline, 'left')
    monoRight = getMonoCamera(pipeline, 'right')

    stereo = getStereoPair(pipeline, monoLeft, monoRight)

    # Disparity xLink
    xoutDisp = pipeline.createXLinkOut()
    xoutDisp.setStreamName('disparity')

    # Creating the xoutlinks
    xoutRight = pipeline.createXLinkOut()
    xoutRight.setStreamName("right")

    xoutLeft = pipeline.createXLinkOut()
    xoutLeft.setStreamName("left")

    # Attaching the xlinks to stereo
    stereo.disparity.link(xoutDisp.input)
    stereo.rectifiedLeft.link(xoutLeft.input)
    stereo.rectifiedRight.link(xoutRight.input)

    with dai.Device(pipeline) as device:
        # Getting output Queues and setting the queue size to 1
        disparityQueue = device.getOutputQueue(
            name='disparity', maxSize=1, blocking=False)
        leftQueue = device.getOutputQueue(
            name='left', maxSize=1, blocking=False)
        rightQueue = device.getOutputQueue(
            name='right', maxSize=1, blocking=False)

        # calculate multiplier for color map
        disparityMultiplier = 255 / stereo.getMaxDisparity()

        # Creating a Window
        cv2.namedWindow("Stereo Pair")
        cv2.namedWindow('Disparity')
        cv2.setMouseCallback('Stereo Pair', mouseCallback)

        # SideBySide variable
        SideBySide = False

        while True:
            # Getting the Frames
            disparity = getFrame(disparityQueue)

            # Colormap
            disparity = (disparity * disparityMultiplier).astype(np.uint8)
            disparity = cv2.applyColorMap(disparity, cv2.COLORMAP_JET)

            # Fetching the individual Frames
            leftFrame = getFrame(leftQueue)
            rightFrame = getFrame(rightQueue)

            if SideBySide:
                imOut = np.hstack((leftFrame, rightFrame))
            else:
                imOut = np.uint8(leftFrame/2 + rightFrame/2)

            imOut = cv2.cvtColor(imOut, cv2.COLOR_GRAY2RGB)

            imOut = cv2.line(imOut, (mouseX, mouseY),
                             (1280, mouseY), (0, 0, 255), 2)
            imOut = cv2.circle(imOut, (mouseX, mouseY), 2, (255, 255, 128), 2)
            # Displaying the frames
            cv2.imshow("Stereo Pair", imOut)
            cv2.imshow('Disparity', disparity)

            key = cv2.waitKey(1)

            if key == ord('q'):
                break
            elif key == ord('t'):
                SideBySide = not SideBySide
            elif key == ord('s'):
                cv2.imwrite('savedImage.png', imOut)
