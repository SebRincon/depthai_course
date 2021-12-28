import dearpygui.dearpygui as dpg
import numpy as np
import depthai as dai
import cv2


def getFrameInfo(frame):
    print("Frame Array")
    print("Frame Type: ", type(frame))
    print("Frame dimensions: ", frame.ndim)
    print("Frame Shape: ", frame.shape)
    print("Frame Size: ", frame.size)
    print("Frame dType: ", frame.dtype)


def FrameFormatter(frame):
    getFrameInfo(frame)
    height, width = frame.shape
    print('Shape: ', height, width)
    # data = np.flip(frame, 1)  # Flip array values from BGR to RGB
    data = frame.ravel()     # flatten data from a 3D to a 1D structure
    data = np.asfarray(data, dtype='f')  # change the data to 32bit floats
    # nomalize the data to prepate for GPU
    texture_data = np.true_divide(data, 255.0)
    print('')
    getFrameInfo(texture_data)
    return {'texture': texture_data, "width": width, "height": height}


def getFrame(queue):
    frame = queue.get()
    return frame.getCvFrame()


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


def disparityImage():

    # Defineing the pipeline
    pipeline = dai.Pipeline()

    # Defining the monoCameras
    monoLeft = getMonoCamera(pipeline, 'left')
    monoRight = getMonoCamera(pipeline, 'right')

    # Creating the xoutlinks
    xoutRight = pipeline.createXLinkOut()
    xoutRight.setStreamName("right")

    xoutLeft = pipeline.createXLinkOut()
    xoutLeft.setStreamName("left")

    # Attaching the cameras to the xoutLinks
    monoLeft.out.link(xoutLeft.input)
    monoRight.out.link(xoutRight.input)

    with dai.Device(pipeline) as device:
        # Getting output Queues and setting the queue size to 1
        leftQueue = device.getOutputQueue(name='left', maxSize=1)
        rightQueue = device.getOutputQueue(name='right', maxSize=1)

        # SideBySide variable
        SideBySide = False

        while True:
            # Getting the Frames
            leftFrame = getFrame(leftQueue)
            rightFrame = getFrame(rightQueue)

            if SideBySide:
                imOut = np.hstack((leftFrame, rightFrame))
            else:
                imOut = np.uint8(leftFrame/2 + rightFrame/2)

            return FrameFormatter(imOut)
            # print(type(imOut))
            # getFrameInfo(imOut)
