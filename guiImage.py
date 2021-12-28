import dearpygui.dearpygui as dpg
import cv2
import numpy as np

vid = cv2.VideoCapture(0)
ret, frame = vid.read()
data = np.flip(frame, 2)  # Flip array values from BGR to RGB
data = data.ravel()     # flatten data from a 3D to a 1D structure
data = np.asfarray(data, dtype='f')  # change the data to 32bit floats
# nomalize the data to prepate for GPU
texture_data = np.true_divide(data, 255.0)


frame_width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(type(frame))

dpg.create_context()
dpg.create_viewport(title='Window', width=1200, height=800)

with dpg.texture_registry(show=True):
    dpg.add_raw_texture(frame_width, frame_height, texture_data,
                        format=dpg.mvFormat_Float_rgb, tag="camera", label='CameraFeed')
with dpg.window(label='Image View'):
    dpg.add_image("camera")

dpg.show_viewport()
dpg.setup_dearpygui()
while dpg.is_dearpygui_running():

    ret, frame = vid.read()
    data = np.flip(frame, 2)  # Flip array values from BGR to RGB
    data = data.ravel()     # flatten data from a 3D to a 1D structure
    data = np.asfarray(data, dtype='f')  # change the data to 32bit floats
    # nomalize the data to prepate for GPU
    texture_data = np.true_divide(data, 255.0)
    dpg.set_value('camera', texture_data)
    dpg.render_dearpygui_frame()

vid.release()
dpg.destroy_context()
# dpg.start_dearpeargui()
