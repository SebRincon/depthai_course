import depthai as dai
import cv2
#creating pipeline
pipeline = dai.Pipeline()

#opening node to the mono camera and setting the camera to the left
mono = pipeline.createMonoCamera()
mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
#interal connection called xlinkin is created with host

#Creating an xlinkout and adding a name
xout = pipeline.createXLinkOut()
xout.setStreamName("left")
#attaching the output of the camera and inputing to the xlinkout
mono.out.link(xout.input)

#       ┌──────OAK D───────────┐
#    ┌──┴──────┐           ┌───┴────┐
#    │Left Mono│◀──────────│XLinkIn │
#    │ Camera  │─────┐     └───┬────┘
#    └──┬──────┘     │     ┌───┴────┐
#       │            └────▶│XLinkOut│───────────┐
#       │                  └───┬────┘           │
#       └──────────────────────┘                │
# ┌──────────────────────────────────────────┐  │
# │cv2 output <- getCvFrame <- Frame <- Queue│◀─┘
# └──────────────────────────────────────────┘

with dai.Device(pipeline) as device:
	#attaching the pipeline to the device and starting a queue to fetch info
	queue = device.getOutputQueue(name='left')
	frame = queue.get()

	cv2.namedWindow("image")
	while True:

		imOut = frame.getCvFrame()
		cv2.imshow("image", imOut)



