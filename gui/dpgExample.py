import dearpygui.dearpygui as dpg
import cv2 as cv
import numpy as np

#     ┌────────────────┐
#     │cv2.VideoCapture│──┐
#     └────────────────┘  │
#           ┌─────┐      vid.Read()──────────────────────────┐
#     ┌─────│frame│◀──────┘                                  │
#     │     └─────┘                                          │
#     │        Flattening -> 32bit float GPU normal data     │
#     └─▶┌─────────────────────────────────────────────────┐ │
#        │data = np.flip(frame, 2)                         │ │
#        │data = data.ravel()                              │ │
#        │data = np.asfarray(data, dtype='f')              │ │
#        │texture_data = np.true_divide(data, 255.0)       │ │
#     ┌──┤frame_width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)  │ │
#     │  │frame_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)│ │
#     │  └─────────────────────────────────────────────────┘ │
#     └─▶┌────────────┐                                      │
#     ┌──│raw_texture │                                      │
#     │  └────────────┘                                      │
# dpg.add_raw_texture()                       ┌──────────────┴────────┐
#     │  ┌────────────────────────────┐       │While Running:         │
#     │  │ Context & Viewport Created │──┐    │-recall frame formatter│
#     │  └────────────────────────────┘  │    └──────────────┬────────┘
#     │  ┌───────────────────┐           │    ┌───────────┐  │
#     └─▶│ Texture Register  │◀──────────┤◀───│Render Loop│◀─┘
#        └───────────────────┘           │    └───────────┘
#        ┌───────────────────┐           │
#        │   Image Viewer    │◀──────────┤
#        └───────────────────┘           │
#      ┌─────────────────────┐           │
#      │Setup & Show viewport│◀──────────┘
#      └─────────────────────┘


dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=800)
dpg.setup_dearpygui()


vid = cv.VideoCapture(0)
ret, frame = vid.read()

# image size or you can get this from image shape
frame_width = vid.get(cv.CAP_PROP_FRAME_WIDTH)
frame_height = vid.get(cv.CAP_PROP_FRAME_HEIGHT)
video_fps = vid.get(cv.CAP_PROP_FPS)
print(frame_width)
print(frame_height)
print(video_fps)

print("Frame Array:")
print("Array is of type: ", type(frame))
print("No. of dimensions: ", frame.ndim)
print("Shape of array: ", frame.shape)
print("Size of array: ", frame.size)
print("Array stores elements of type: ", frame.dtype)
# because the camera data comes in as BGR and we need RGB
data = np.flip(frame, 2)
data = data.ravel()  # flatten camera data to a 1 d stricture
data = np.asfarray(data, dtype='f')  # change data type to 32bit floats
# normalize image data to prepare for GPU
texture_data = np.true_divide(data, 255.0)

print("texture_data Array:")
print("Array is of type: ", type(texture_data))
print("No. of dimensions: ", texture_data.ndim)
print("Shape of array: ", texture_data.shape)
print("Size of array: ", texture_data.size)
print("Array stores elements of type: ", texture_data.dtype)

with dpg.texture_registry(show=True):
    dpg.add_raw_texture(frame.shape[1], frame.shape[0], texture_data,
                        tag="texture_tag", format=dpg.mvFormat_Float_rgb)

with dpg.window(label="Example Window"):
    dpg.add_text("Hello, world")
    dpg.add_image("texture_tag")

dpg.show_metrics()
dpg.show_viewport()
while dpg.is_dearpygui_running():

    # updating the texture in a while loop the frame rate will be limited to the camera frame rate.
    # commenting out the "ret, frame = vid.read()" line will show the full speed that operations and updating a texture can run at

    ret, frame = vid.read()
    data = np.flip(frame, 2)
    data = data.ravel()
    data = np.asfarray(data, dtype='f')
    texture_data = np.true_divide(data, 255.0)
    dpg.set_value("texture_tag", texture_data)

    # to compare to the base example in the open cv tutorials uncomment below
    #cv.imshow('frame', frame)
    dpg.render_dearpygui_frame()

vid.release()
# cv.destroyAllWindows() # when using upen cv window "imshow" call this also
dpg.destroy_context()
