import dearpygui.dearpygui as dpg
import depthai as dai
import numpy as np
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
    #print('Shape: ', height, width)
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

#    cv2.namedWindow("Window")

    # Getting the Frames
    leftFrame = getFrame(leftQueue)
    rightFrame = getFrame(rightQueue)

    image = np.uint8(leftFrame/2 + rightFrame/2)
    texture_data = FrameFormatter(image)

    dpg.create_context()
    dpg.create_viewport(title='Window', width=1000, height=600)

    with dpg.texture_registry(show=True):
        dpg.add_raw_texture(texture_data["width"], texture_data["height"], texture_data["texture"],
                            format=dpg.mvFormat_Float_rgb, tag="camera", label='CameraFeed')

    with dpg.window(label='Image View'):
        dpg.add_image("camera")

    dpg.setup_dearpygui()
    dpg.show_viewport()

    flow = True

    while dpg.is_dearpygui_running():

        if flow:
            leftFrame = getFrame(leftQueue)
            rightFrame = getFrame(rightQueue)
            image = np.uint8(leftFrame/2 + rightFrame/2)

            texture_data = FrameFormatter(image)
            dpg.set_value('camera', texture_data['texture'])
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
