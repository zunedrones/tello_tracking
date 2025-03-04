# tello_tracking

Project using the Tello drone to track a predetermined object, using the [DJITellopy library](https://github.com/damiafuentes/DJITelloPy/tree/master). The model was trained using YOLOv8m.

For now, the project only detect using YOLO model.

![image](https://github.com/user-attachments/assets/925e0983-29f8-493d-b752-966b26e1f6ff)

# Requeriments

* Python >= 3.9.0

```bash
pip install ultralytics
```
```bash
pip install opencv-python
```
```bash
pip install djitellopy==2.4.0
```
```bash
pip install "numpy<2"
```

# Run the project

```bash
git clone -b djitellopy https://github.com/zunedrones/tello_tracking.git
cd tello_tracking
python main.py
```
* You need to be connected to the Tello's Wi-Fi network to run the program.
