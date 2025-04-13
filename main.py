import sys
import cv2
from deepface import DeepFace
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage,QIcon
from PySide6.QtCore import Qt
import qdarkstyle

class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)

        self.toggle_button = QToolButton(text=title)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QWidget()
        self.content_area.setVisible(False) 

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 5, 5, 5)  

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

    def on_toggle(self):
        expanded = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_area.setVisible(expanded)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

class FaceDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asian Face Detector")
        self.setWindowIcon(QIcon('icon.png'))

        self.data = QLabel("")
        self.extra_data = QLabel("")
        self.image_label = QLabel("Load an image to detect faces")
        self.data.setAlignment(Qt.AlignHCenter)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)

        
        self.collapsible = CollapsibleBox("More Details")
        self.collapsible.add_widget(self.extra_data)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.data)
        layout.addWidget(self.collapsible)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.detect_race(file_name)

    def detect_race(self,image_path):
        result = DeepFace.analyze(
        img_path = image_path, 
        actions = ['race'],
        enforce_detection=False
        )
        if not result or not result[0]:
            self.data.setText("No Face Detected!")
            return
        
        region = result[0]['region']
        x,y,w,h = region['x'],region['y'],region['w'],region['h']
        print(result)
        print(x,y,w,h)

        # draw rectangle around detected face region
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Convert to Qt image format
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Show image
        self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(600, 400, Qt.KeepAspectRatio))

        race_scores = result[0]['race']
        print("Race Scores:", race_scores)

        extra_data=""

        sorted_races = sorted(race_scores.items(), key=lambda x: x[1], reverse=True)
        for race, score in sorted_races:
            extra_data += f"{race}: {score:.2f}%\n"
            print(f"{race}: {score:.2f}%")

        self.extra_data.setText(extra_data)
        threshold = 20 

        top_races = sorted(race_scores.items(), key=lambda x: x[1], reverse=True)[:2]

        dominant_race, dominant_score = top_races[0]
        second_race, second_score = top_races[1]

        if second_score >= threshold:
            self.data.setText(f"Possible mixed ethnicity: {dominant_race} + {second_race}".title())
        else:
            self.data.setText(f"Pure {dominant_race} face detected".title())

# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet('pyside6'))
    window = FaceDetectorApp()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
