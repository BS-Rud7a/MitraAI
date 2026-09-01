import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel
)

from Brain.brain import mitra_response


class MitraWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mitra AI")
        self.resize(700, 700)

        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Mitra AI")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        main_layout.addWidget(title)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        main_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Type a message to Mitra..."
        )

        self.send_button = QPushButton("Send")

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

        # Connect button
        self.send_button.clicked.connect(
            self.send_message
        )

        # Pressing Enter also sends
        self.message_input.returnPressed.connect(
            self.send_message
        )

    def send_message(self):

        user_message = self.message_input.text().strip()

        if not user_message:
            return

        # Display user's message
        self.chat_display.append(
            f"<b>You:</b> {user_message}"
        )

        # Clear input
        self.message_input.clear()

        # Get Mitra's response
        response = mitra_response(user_message)

        # Display Mitra's response
        self.chat_display.append(
            f"<b>Mitra:</b> {response}"
        )


def main():

    app = QApplication(sys.argv)

    window = MitraWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()