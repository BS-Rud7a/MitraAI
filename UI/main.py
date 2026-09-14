import sys
import os

from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    QPoint
)

from PySide6.QtGui import QPixmap

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QDialog,
    QComboBox,
    QCheckBox,
    QFormLayout,
    QDialogButtonBox,
    QTextEdit
)

from Brain.brain import mitra_response
from Brain.memory import load_memory
from Voice.tts import speak, set_speech_callbacks
from stt import speech_to_text


# =========================================================
# BRAIN WORKER
# =========================================================

class MitraWorker(QThread):

    response_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, message):

        super().__init__()

        self.message = message

    def run(self):

        try:

            result = mitra_response(
                self.message
            )

            self.response_ready.emit(
                result
            )

        except Exception as error:

            self.error_occurred.emit(
                str(error)
            )


# =========================================================
# TTS WORKER
# =========================================================

class TTSWorker(QThread):

    finished = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        text,
        language
    ):

        super().__init__()

        self.text = text
        self.language = language

    def run(self):

        try:

            speak(
                self.text,
                self.language
            )

        except Exception as error:

            self.error_occurred.emit(
                str(error)
            )

        finally:

            self.finished.emit()


# =========================================================
# STT WORKER
# =========================================================

class STTWorker(QThread):

    transcription_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, language="en"):

        super().__init__()

        self.language = language

    def run(self):

        try:

            result = speech_to_text(self.language)

            self.transcription_ready.emit(result)

        except Exception as error:

            self.error_occurred.emit(str(error))


# =========================================================
# CHAT BUBBLE
# =========================================================

class ChatBubble(QFrame):

    def __init__(
        self,
        message,
        is_user=False
    ):

        super().__init__()

        if is_user:

            self.setObjectName(
                "userBubble"
            )

        else:

            self.setObjectName(
                "mitraBubble"
            )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            18,
            13,
            18,
            13
        )

        layout.setSpacing(
            0
        )

        text = QLabel(
            message
        )

        text.setWordWrap(
            True
        )

        text.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        if is_user:

            text.setObjectName(
                "userBubbleText"
            )

        else:

            text.setObjectName(
                "mitraBubbleText"
            )

        layout.addWidget(
            text
        )

        self.setLayout(
            layout
        )

        self.setMaximumWidth(
            500
        )

        self.setSizePolicy(
            QSizePolicy.Maximum,
            QSizePolicy.Minimum
        )


# =========================================================
# SETTINGS WINDOW
# =========================================================

class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Mitra Settings")
        self.setFixedSize(420, 410)

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Mitra Settings")
        title.setObjectName("settingsTitle")

        subtitle = QLabel("Customize how Mitra behaves.")
        subtitle.setObjectName("settingsSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        form = QFormLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(16)

        language = QComboBox()
        language.addItem("Auto", None)
        language.addItem("English", "en")
        language.addItem("Hindi / Hinglish", "hi")
        language.setCurrentIndex(0)
        language.setFixedHeight(38)

        voice = QComboBox()
        voice.addItem("F1")
        voice.setFixedHeight(38)

        memory = QCheckBox("Remember important things")
        memory.setChecked(True)

        self.view_memories_button = QPushButton(
            "View Memories"
        )

        self.view_memories_button.setObjectName(
            "viewMemoriesButton"
        )

        self.view_memories_button.setFixedHeight(
            38
        )

        self.view_memories_button.clicked.connect(
            self.view_memories
        )

        form.addRow("Voice input:", language)
        form.addRow("Voice:", voice)
        form.addRow("Memory:", memory)
        form.addRow("", self.view_memories_button)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout.addWidget(buttons)

        self.setLayout(layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #0B0D11;
                color: #F3F4F6;
            }

            QLabel#settingsTitle {
                background-color: transparent;
                color: #F3F4F6;
                font-size: 22px;
                font-weight: 600;
            }

            QLabel#settingsSubtitle {
                background-color: transparent;
                color: #747B88;
                font-size: 12px;
            }

            QLabel {
                background-color: transparent;
                color: #A1A7B2;
                font-size: 13px;
            }

            QComboBox {
                background-color: #171A20;
                color: #F3F4F6;
                border: 1px solid #2A2F38;
                border-radius: 10px;
                padding: 0 10px;
            }

            QComboBox:hover {
                border-color: #414752;
            }

            QComboBox QAbstractItemView {
                background-color: #171A20;
                color: #F3F4F6;
                selection-background-color: #303640;
            }

            QCheckBox {
                background-color: transparent;
                color: #A1A7B2;
                font-size: 13px;
            }

            QPushButton#viewMemoriesButton {
                background-color: #242932;
                color: #F0F1F3;
                border: 1px solid #2D323C;
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 12px;
            }

            QPushButton#viewMemoriesButton:hover {
                background-color: #303640;
                border-color: #414752;
            }

            QPushButton#viewMemoriesButton:pressed {
                background-color: #3A404B;
            }

            QDialogButtonBox QPushButton {
                background-color: #242932;
                color: #F0F1F3;
                border: none;
                border-radius: 10px;
                padding: 8px 18px;
            }

            QDialogButtonBox QPushButton:hover {
                background-color: #303640;
            }
        """)


    # =====================================================
    # VIEW MEMORIES
    # =====================================================

    def view_memories(self):

        try:

            memory = load_memory()

            facts = memory.get(
                "facts",
                []
            )

            user_name = memory.get(
                "user_name",
                ""
            ).strip()

            dialog = QDialog(self)
            dialog.setWindowTitle(
                "Mitra Memories"
            )
            dialog.setFixedSize(
                520,
                500
            )

            layout = QVBoxLayout()
            layout.setContentsMargins(
                28,
                24,
                28,
                24
            )
            layout.setSpacing(
                14
            )

            title = QLabel(
                "Mitra's Memories"
            )
            title.setObjectName(
                "memoryTitle"
            )

            subtitle = QLabel(
                "Things Mitra currently remembers."
            )
            subtitle.setObjectName(
                "memorySubtitle"
            )

            layout.addWidget(
                title
            )

            layout.addWidget(
                subtitle
            )

            if user_name:

                name_label = QLabel(
                    f"Name: {user_name}"
                )

                name_label.setObjectName(
                    "memoryName"
                )

                layout.addWidget(
                    name_label
                )

            memory_text = QTextEdit()
            memory_text.setReadOnly(
                True
            )
            memory_text.setObjectName(
                "memoryText"
            )

            if facts:

                lines = []

                for index, fact in enumerate(
                    facts,
                    start=1
                ):

                    lines.append(
                        f"• {fact}"
                    )

                memory_text.setPlainText(
                    "\n\n".join(lines)
                )

            else:

                memory_text.setPlainText(
                    "Mitra hasn't saved any facts yet."
                )

            layout.addWidget(
                memory_text
            )

            close_button = QPushButton(
                "Close"
            )

            close_button.setFixedHeight(
                38
            )

            close_button.clicked.connect(
                dialog.accept
            )

            layout.addWidget(
                close_button
            )

            dialog.setLayout(
                layout
            )

            dialog.setStyleSheet("""
                QDialog {
                    background-color: #0B0D11;
                    color: #F3F4F6;
                }

                QLabel {
                    background-color: transparent;
                }

                QLabel#memoryTitle {
                    color: #F3F4F6;
                    font-size: 22px;
                    font-weight: 600;
                }

                QLabel#memorySubtitle {
                    color: #747B88;
                    font-size: 12px;
                }

                QLabel#memoryName {
                    color: #A1A7B2;
                    font-size: 13px;
                }

                QTextEdit#memoryText {
                    background-color: #171A20;
                    color: #F3F4F6;
                    border: 1px solid #2A2F38;
                    border-radius: 12px;
                    padding: 12px;
                    font-size: 13px;
                }

                QPushButton {
                    background-color: #242932;
                    color: #F0F1F3;
                    border: 1px solid #2D323C;
                    border-radius: 10px;
                    padding: 8px 18px;
                    font-size: 12px;
                }

                QPushButton:hover {
                    background-color: #303640;
                    border-color: #414752;
                }

                QPushButton:pressed {
                    background-color: #3A404B;
                }
            """)

            dialog.exec()

        except Exception as error:

            print(
                "Memory viewer error:",
                error
            )


# =========================================================
# MITRA WINDOW
# =========================================================

class MitraWindow(QWidget):

    speech_started = Signal()
    speech_finished = Signal()

    def __init__(self):

        super().__init__()

        self.worker = None
        self.tts_worker = None
        self.stt_worker = None

        self.is_speaking = False
        self.is_listening = False

        # -------------------------------------------------
        # Avatar assets
        # -------------------------------------------------

        assets_path = os.path.join(
            os.path.dirname(__file__),
            "assets"
        )

        self.avatar_images = {

            "idle": os.path.join(
                assets_path,
                "mitra_idle.png"
            ),

            "thinking": os.path.join(
                assets_path,
                "mitra_thinking.png"
            ),

            "speaking": os.path.join(
                assets_path,
                "mitra_speaking.png"
            )
        }

        # -------------------------------------------------
        # Avatar animation
        # -------------------------------------------------

        self.avatar_animation = None

        self.avatar_base_position = None

        # -------------------------------------------------
        # Setup
        # -------------------------------------------------

        self.setup_window()

        self.setup_ui()

        self.apply_styles()

        # -------------------------------------------------
        # TTS callbacks
        # -------------------------------------------------

        set_speech_callbacks(
            on_start=self.speech_started.emit,
            on_finish=self.speech_finished.emit
        )

        self.speech_started.connect(
            self.on_speech_started
        )

        self.speech_finished.connect(
            self.on_speech_finished
        )

        # Start idle animation
        self.start_avatar_animation(
            "idle"
        )

    # =====================================================
    # WINDOW
    # =====================================================

    def setup_window(self):

        self.setWindowTitle(
            "Mitra AI"
        )

        self.resize(
            1200,
            750
        )

        self.setMinimumSize(
            950,
            600
        )

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # =================================================
        # HEADER
        # =================================================

        header = QFrame()

        header.setObjectName(
            "header"
        )

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            30,
            18,
            30,
            18
        )

        header_layout.setSpacing(
            10
        )

        logo = QLabel(
            "✦"
        )

        logo.setObjectName(
            "logo"
        )

        title = QLabel(
            "MITRA"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "AI COMPANION"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        title_layout = QVBoxLayout()

        title_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        title_layout.setSpacing(
            0
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header_layout.addWidget(
            logo
        )

        header_layout.addLayout(
            title_layout
        )

        header_layout.addStretch()

        online = QLabel(
            "●  ONLINE"
        )

        online.setObjectName(
            "online"
        )

        header_layout.addWidget(
            online
        )

        header_layout.addSpacing(
            20
        )

        self.clear_button = QPushButton(
            "Clear"
        )

        self.clear_button.setObjectName(
            "clearButton"
        )

        self.clear_button.clicked.connect(
            self.clear_chat
        )

        header_layout.addWidget(
            self.clear_button
        )

        self.settings_button = QPushButton(
            "⚙"
        )

        self.settings_button.setObjectName(
            "settingsButton"
        )

        self.settings_button.setFixedSize(
            42,
            42
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )

        header_layout.addWidget(
            self.settings_button
        )

        header.setLayout(
            header_layout
        )

        main_layout.addWidget(
            header
        )

        # =================================================
        # MAIN CONTENT
        # =================================================

        content = QHBoxLayout()

        content.setContentsMargins(
            0,
            0,
            0,
            0
        )

        content.setSpacing(
            0
        )

        # =================================================
        # AVATAR PANEL
        # =================================================

        avatar_panel = QFrame()

        avatar_panel.setObjectName(
            "avatarPanel"
        )

        avatar_layout = QVBoxLayout()

        avatar_layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        avatar_layout.setAlignment(
            Qt.AlignCenter
        )

        greeting = QLabel(
            "YOUR COMPANION"
        )

        greeting.setObjectName(
            "avatarGreeting"
        )

        greeting.setAlignment(
            Qt.AlignCenter
        )

        avatar_layout.addWidget(
            greeting
        )

        avatar_layout.addSpacing(
            25
        )

        # -------------------------------------------------
        # Avatar card
        # -------------------------------------------------

        avatar_card = QFrame()

        avatar_card.setObjectName(
            "avatarCard"
        )

        avatar_card_layout = QVBoxLayout()

        avatar_card_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        self.avatar = QLabel()

        self.avatar.setObjectName(
            "avatar"
        )

        self.avatar.setAlignment(
            Qt.AlignCenter
        )

        self.avatar.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.load_avatar()

        avatar_card_layout.addWidget(
            self.avatar
        )

        avatar_card.setLayout(
            avatar_card_layout
        )

        avatar_card.setFixedWidth(390)

        avatar_layout.addWidget(
            avatar_card,
            0,
            Qt.AlignHCenter
        )

        avatar_layout.addSpacing(
            20
        )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------

        name = QLabel(
            "Mitra"
        )

        name.setObjectName(
            "avatarName"
        )

        name.setAlignment(
            Qt.AlignCenter
        )

        avatar_layout.addWidget(
            name
        )

        avatar_layout.addSpacing(
            5
        )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        self.avatar_status = QLabel(
            "● Ready to chat"
        )

        self.avatar_status.setObjectName(
            "avatarStatus"
        )

        self.avatar_status.setAlignment(
            Qt.AlignCenter
        )

        avatar_layout.addWidget(
            self.avatar_status
        )

        avatar_layout.addStretch()

        avatar_panel.setLayout(
            avatar_layout
        )

        content.addWidget(
            avatar_panel,
            1
        )

        # =================================================
        # CHAT PANEL
        # =================================================

        chat_panel = QFrame()

        chat_panel.setObjectName(
            "chatPanel"
        )

        chat_layout = QVBoxLayout()

        chat_layout.setContentsMargins(
            35,
            30,
            35,
            25
        )

        chat_layout.setSpacing(
            0
        )

        chat_title = QLabel(
            "Conversation"
        )

        chat_title.setObjectName(
            "chatTitle"
        )

        chat_subtitle = QLabel(
            "Talk naturally. Mitra remembers what matters."
        )

        chat_subtitle.setObjectName(
            "chatSubtitle"
        )

        chat_layout.addWidget(
            chat_title
        )

        chat_layout.addSpacing(
            5
        )

        chat_layout.addWidget(
            chat_subtitle
        )

        chat_layout.addSpacing(
            20
        )

        # =================================================
        # SCROLL AREA
        # =================================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll_area.setObjectName(
            "scrollArea"
        )

        self.chat_container = QWidget()

        self.chat_container.setObjectName(
            "chatContainer"
        )

        self.chat_layout = QVBoxLayout()

        self.chat_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.chat_layout.setSpacing(
            18
        )

        # =================================================
        # WELCOME
        # =================================================

        self.welcome_widget = QWidget()

        welcome_layout = QVBoxLayout()

        welcome_layout.setAlignment(
            Qt.AlignCenter
        )

        welcome_icon = QLabel(
            "✦"
        )

        welcome_icon.setObjectName(
            "welcomeIcon"
        )

        welcome_icon.setAlignment(
            Qt.AlignCenter
        )

        welcome_title = QLabel(
            "Welcome to Mitra"
        )

        welcome_title.setObjectName(
            "welcomeTitle"
        )

        welcome_title.setAlignment(
            Qt.AlignCenter
        )

        welcome_subtitle = QLabel(
            "Your friendly AI companion"
        )

        welcome_subtitle.setObjectName(
            "welcomeSubtitle"
        )

        welcome_subtitle.setAlignment(
            Qt.AlignCenter
        )

        welcome_hint = QLabel(
            "Say hello and start a conversation. 😊"
        )

        welcome_hint.setObjectName(
            "welcomeHint"
        )

        welcome_hint.setAlignment(
            Qt.AlignCenter
        )

        welcome_layout.addWidget(
            welcome_icon
        )

        welcome_layout.addSpacing(
            10
        )

        welcome_layout.addWidget(
            welcome_title
        )

        welcome_layout.addWidget(
            welcome_subtitle
        )

        welcome_layout.addSpacing(
            15
        )

        welcome_layout.addWidget(
            welcome_hint
        )

        self.welcome_widget.setLayout(
            welcome_layout
        )

        self.chat_layout.addWidget(
            self.welcome_widget
        )

        self.chat_layout.addStretch()

        self.chat_container.setLayout(
            self.chat_layout
        )

        self.scroll_area.setWidget(
            self.chat_container
        )

        chat_layout.addWidget(
            self.scroll_area
        )

        # =================================================
        # INPUT
        # =================================================

        chat_layout.addSpacing(
            15
        )

        input_frame = QFrame()

        input_frame.setObjectName(
            "inputFrame"
        )

        input_layout = QHBoxLayout()

        input_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        input_layout.setSpacing(
            8
        )

        self.message_input = QLineEdit()

        self.message_input.setObjectName(
            "messageInput"
        )

        self.message_input.setPlaceholderText(
            "Write something to Mitra..."
        )

        self.mic_button = QPushButton(
            "🎤"
        )

        self.mic_button.setObjectName(
            "micButton"
        )

        self.mic_button.setFixedSize(
            50,
            50
        )

        self.send_button = QPushButton(
            "➤"
        )

        self.send_button.setObjectName(
            "sendButton"
        )

        self.send_button.setFixedSize(
            50,
            50
        )

        input_layout.addWidget(
            self.message_input
        )

        input_layout.addWidget(
            self.mic_button
        )

        input_layout.addWidget(
            self.send_button
        )

        input_frame.setLayout(
            input_layout
        )

        chat_layout.addWidget(
            input_frame
        )

        chat_panel.setLayout(
            chat_layout
        )

        content.addWidget(
            chat_panel,
            2
        )

        main_layout.addLayout(
            content
        )

        self.setLayout(
            main_layout
        )

        # =================================================
        # CONNECTIONS
        # =================================================

        self.send_button.clicked.connect(
            self.send_message
        )

        self.mic_button.clicked.connect(
            self.start_listening
        )

        self.message_input.returnPressed.connect(
            self.send_message
        )


    # =====================================================
    # SETTINGS
    # =====================================================

    def open_settings(self):

        if self.is_speaking or self.is_listening:
            return

        dialog = SettingsDialog(self)

        dialog.exec()


    # =====================================================
    # LOAD AVATAR
    # =====================================================

    def load_avatar(self):

        self.set_avatar_state(
            "idle"
        )

    # =====================================================
    # SET AVATAR STATE
    # =====================================================

    def set_avatar_state(
        self,
        state
    ):

        avatar_path = self.avatar_images.get(
            state
        )

        if not avatar_path:

            return

        if not os.path.exists(
            avatar_path
        ):

            print(
                f"Avatar image not found: {avatar_path}"
            )

            return

        pixmap = QPixmap(
            avatar_path
        )

        pixmap = pixmap.scaled(
            330,
            430,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.avatar.setPixmap(
            pixmap
        )

    # =====================================================
    # AVATAR ANIMATION
    # =====================================================

    def start_avatar_animation(
        self,
        state
    ):

        # Stop existing animation
        if self.avatar_animation:

            self.avatar_animation.stop()

        # Save the current position
        if self.avatar_base_position is None:

            self.avatar_base_position = (
                self.avatar.pos()
            )

        base_position = (
            self.avatar_base_position
        )

        # -------------------------------------------------
        # Animation settings
        # -------------------------------------------------

        if state == "idle":

            distance = 4
            duration = 2400

        elif state == "thinking":

            distance = 6
            duration = 1400

        elif state == "speaking":

            distance = 5
            duration = 700

        else:

            distance = 4
            duration = 2400

        # -------------------------------------------------
        # Create animation
        # -------------------------------------------------

        self.avatar_animation = QPropertyAnimation(
            self.avatar,
            b"pos"
        )

        self.avatar_animation.setDuration(
            duration
        )

        self.avatar_animation.setStartValue(
            base_position
        )

        self.avatar_animation.setEndValue(
            QPoint(
                base_position.x(),
                base_position.y() - distance
            )
        )

        self.avatar_animation.setEasingCurve(
            QEasingCurve.InOutSine
        )

        self.avatar_animation.setLoopCount(
            -1
        )

        self.avatar_animation.start()

    # =====================================================
    # START LISTENING
    # =====================================================

    def start_listening(self):

        if self.is_speaking or self.is_listening:
            return

        self.is_listening = True

        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.mic_button.setEnabled(False)

        self.set_avatar_state(
            "speaking"
        )

        self.start_avatar_animation(
            "speaking"
        )

        self.avatar_status.setText(
            "● Listening..."
        )

        self.stt_worker = STTWorker(
            None
        )

        self.stt_worker.transcription_ready.connect(
            self.receive_transcription
        )

        self.stt_worker.error_occurred.connect(
            self.handle_stt_error
        )

        self.stt_worker.finished.connect(
            self.stt_finished
        )

        self.stt_worker.start()

    # =====================================================
    # RECEIVE TRANSCRIPTION
    # =====================================================

    def receive_transcription(self, result):

        if not result:
            return

        message = result.get(
            "text", ""
        ).strip()

        if not message:
            return

        self.send_message(
            message
        )

    # =====================================================
    # STT FINISHED
    # =====================================================

    def stt_finished(self):

        self.is_listening = False

        # If the transcription was sent to the Brain, keep
        # the existing thinking state until the Brain finishes.
        if self.worker is not None and self.worker.isRunning():

            return

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.avatar_status.setText(
            "● Ready to chat"
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.mic_button.setEnabled(
            True
        )

    # =====================================================
    # STT ERROR
    # =====================================================

    def handle_stt_error(self, error):

        print(
            "STT error:",
            error
        )

        self.is_listening = False

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.avatar_status.setText(
            "● Microphone error"
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.mic_button.setEnabled(
            True
        )

    # =====================================================
    # SEND MESSAGE
    # =====================================================

    def send_message(self, message=None):

        if message is None:

            message = (
                self.message_input
                .text()
                .strip()
            )

        else:

            message = message.strip()

        if not message:

            return

        # -------------------------------------------------
        # Hide welcome screen
        # -------------------------------------------------

        self.welcome_widget.hide()

        # -------------------------------------------------
        # Add user message
        # -------------------------------------------------

        self.add_message(
            message,
            True
        )

        # -------------------------------------------------
        # Clear input
        # -------------------------------------------------

        self.message_input.clear()

        # -------------------------------------------------
        # Disable input
        # -------------------------------------------------

        self.message_input.setEnabled(
            False
        )

        self.send_button.setEnabled(
            False
        )

        self.mic_button.setEnabled(
            False
        )

        # -------------------------------------------------
        # Thinking state
        # -------------------------------------------------

        self.set_avatar_state(
            "thinking"
        )

        self.start_avatar_animation(
            "thinking"
        )

        self.avatar_status.setText(
            "● Mitra is thinking..."
        )

        # -------------------------------------------------
        # Start Brain worker
        # -------------------------------------------------

        self.worker = MitraWorker(
            message
        )

        self.worker.response_ready.connect(
            self.receive_response
        )

        self.worker.error_occurred.connect(
            self.handle_error
        )

        self.worker.finished.connect(
            self.brain_finished
        )

        self.worker.start()

    # =====================================================
    # RECEIVE RESPONSE
    # =====================================================

    def receive_response(
        self,
        result
    ):

        # -------------------------------------------------
        # Extract data
        # -------------------------------------------------

        mitra_text = result["text"]

        language = result["language"]

        # -------------------------------------------------
        # Display response
        # -------------------------------------------------

        self.add_message(
            mitra_text,
            False
        )

        # -------------------------------------------------
        # Preparing voice
        # -------------------------------------------------

        self.avatar_status.setText(
            "● Preparing voice..."
        )

        # -------------------------------------------------
        # Start TTS
        # -------------------------------------------------

        self.tts_worker = TTSWorker(
            mitra_text,
            language
        )

        self.tts_worker.error_occurred.connect(
            self.handle_tts_error
        )

        self.tts_worker.finished.connect(
            self.tts_finished
        )

        self.tts_worker.start()

    # =====================================================
    # BRAIN FINISHED
    # =====================================================

    def brain_finished(self):

        pass

    # =====================================================
    # SPEECH STARTED
    # =====================================================

    def on_speech_started(self):

        self.is_speaking = True

        self.set_avatar_state(
            "speaking"
        )

        self.start_avatar_animation(
            "speaking"
        )

        self.avatar_status.setText(
            "● Speaking..."
        )

        self.message_input.setEnabled(
            False
        )

        self.send_button.setEnabled(
            False
        )

    # =====================================================
    # SPEECH FINISHED
    # =====================================================

    def on_speech_finished(self):

        self.is_speaking = False

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.avatar_status.setText(
            "● Ready to chat"
        )

    # =====================================================
    # TTS FINISHED
    # =====================================================

    def tts_finished(self):

        self.is_speaking = False

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.avatar_status.setText(
            "● Ready to chat"
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.mic_button.setEnabled(
            True
        )

        self.message_input.setFocus()

    # =====================================================
    # TTS ERROR
    # =====================================================

    def handle_tts_error(
        self,
        error
    ):

        print(
            "TTS error:",
            error
        )

        self.is_speaking = False

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.avatar_status.setText(
            "● Voice error"
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.mic_button.setEnabled(
            True
        )

        self.message_input.setFocus()

    # =====================================================
    # GENERAL ERROR
    # =====================================================

    def handle_error(
        self,
        error
    ):

        print(
            "Mitra error:",
            error
        )

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.add_message(
            "Something went wrong. Please try again. 😕",
            False
        )

        self.avatar_status.setText(
            "● Connection error"
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.mic_button.setEnabled(
            True
        )

        self.message_input.setFocus()

    # =====================================================
    # ADD MESSAGE
    # =====================================================

    def add_message(
        self,
        message,
        is_user
    ):

        bubble = ChatBubble(
            message,
            is_user
        )

        sender = QLabel(
            "You" if is_user else "Mitra"
        )

        if is_user:

            sender.setObjectName(
                "userSender"
            )

            sender.setAlignment(
                Qt.AlignRight
            )

        else:

            sender.setObjectName(
                "mitraSender"
            )

            sender.setAlignment(
                Qt.AlignLeft
            )

        message_column = QVBoxLayout()

        message_column.setContentsMargins(
            0,
            0,
            0,
            0
        )

        message_column.setSpacing(
            6
        )

        message_column.addWidget(
            sender
        )

        message_column.addWidget(
            bubble
        )

        message_column_widget = QWidget()

        message_column_widget.setLayout(
            message_column
        )

        message_column_widget.setSizePolicy(
            QSizePolicy.Maximum,
            QSizePolicy.Minimum
        )

        row = QHBoxLayout()

        row.setContentsMargins(
            0,
            0,
            0,
            0
        )

        if is_user:

            row.addStretch()

            row.addWidget(
                message_column_widget
            )

        else:

            row.addWidget(
                message_column_widget
            )

            row.addStretch()

        container = QWidget()

        container.setLayout(
            row
        )

        self.chat_layout.insertWidget(
            self.chat_layout.count() - 1,
            container
        )

        QApplication.processEvents()

        scrollbar = (
            self.scroll_area
            .verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    # =====================================================
    # CLEAR CHAT
    # =====================================================

    def clear_chat(self):

        if self.is_speaking:

            return

        while self.chat_layout.count() > 2:

            item = self.chat_layout.takeAt(
                1
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

        self.welcome_widget.show()

        self.set_avatar_state(
            "idle"
        )

        self.start_avatar_animation(
            "idle"
        )

        self.avatar_status.setText(
            "● Ready to chat"
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.message_input.setFocus()

    # =====================================================
    # STYLES
    # =====================================================

    def apply_styles(self):

        self.setStyleSheet("""

        QWidget {
            background-color: #0B0D11;
            color: #F3F4F6;
            font-family: "Segoe UI";
            font-size: 14px;
        }


        /* =================================================
           HEADER
        ================================================= */

        #header {
            background-color: #11141A;
            border-bottom: 1px solid #242832;
        }

        #logo {
            background-color: #0B0D11;
            font-size: 28px;
            padding: 10px 13px;
            border-radius: 10px;
        }

        #title {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 2px;
        }

        #subtitle {
            color: #747B88;
            font-size: 9px;
            letter-spacing: 2px;
        }

        #online {
            color: #70E39A;
            background-color: #0B0D11;
            padding: 14px 16px;
            font-size: 12px;
            letter-spacing: 1px;
        }


        /* =================================================
           CLEAR
        ================================================= */

        #clearButton {
            background-color: transparent;
            color: #858B96;
            border: 1px solid #2D323C;
            border-radius: 10px;
            padding: 8px 14px;
            font-size: 11px;
        }

        #clearButton:hover {
            background-color: #1B1F27;
            color: #F3F4F6;
            border-color: #414752;
        }

        #clearButton:pressed {
            background-color: #242932;
        }

        /* =================================================
           SETTINGS
        ================================================= */

        #settingsButton {
            background-color: transparent;
            color: #858B96;
            border: 1px solid #2D323C;
            border-radius: 10px;
            font-size: 18px;
        }

        #settingsButton:hover {
            background-color: #1B1F27;
            color: #F3F4F6;
            border-color: #414752;
        }

        #settingsButton:pressed {
            background-color: #242932;
        }


        /* =================================================
           AVATAR
        ================================================= */

        #avatarPanel {
            background-color: #0F1217;
            border-right: 1px solid #242832;
        }

        #avatarGreeting {
            color: #727987;
            font-size: 10px;
            letter-spacing: 3px;
            font-weight: 600;
        }

        #avatarCard {
            background-color: #161A21;
            border: 1px solid #292E38;
            border-radius: 28px;
        }

        #avatar {
            background-color: transparent;
            border: none;
        }

        #avatarName {
            background-color: transparent;
            font-size: 25px;
            font-weight: 600;
        }

        #avatarStatus {
            background-color: transparent;
            color: #727987;
            font-size: 12px;
        }


        /* =================================================
           CHAT
        ================================================= */

        #chatPanel {
            background-color: #0C0F14;
        }

        #chatTitle {
            background-color: transparent;
            font-size: 22px;
            font-weight: 600;
        }

        #chatSubtitle {
            background-color: transparent;
            color: #6F7683;
            font-size: 12px;
        }


        /* =================================================
           SCROLL
        ================================================= */

        #scrollArea {
            background-color: transparent;
            border: none;
        }

        #scrollArea > QWidget {
            background-color: transparent;
        }

        #chatContainer {
            background-color: transparent;
        }


        /* =================================================
           WELCOME
        ================================================= */

        #welcomeIcon {
            background-color: transparent;
            color: #F3F4F6;
            font-size: 42px;
        }

        #welcomeTitle {
            background-color: transparent;
            font-size: 28px;
            font-weight: 600;
        }

        #welcomeSubtitle {
            background-color: transparent;
            color: #A1A7B2;
            font-size: 14px;
        }

        #welcomeHint {
            background-color: transparent;
            color: #666D79;
            font-size: 12px;
        }


        /* =================================================
           SENDERS
        ================================================= */

        #userSender {
            background-color: transparent;
            color: #626873;
            font-size: 10px;
            font-weight: 600;
            padding-right: 4px;
        }

        #mitraSender {
            background-color: transparent;
            color: #858C98;
            font-size: 10px;
            font-weight: 600;
            padding-left: 4px;
        }


        /* =================================================
           USER BUBBLE
        ================================================= */

        #userBubble {
            background-color: #E8E9EC;
            border: none;
            border-radius: 18px;
        }

        #userBubbleText {
            background-color: transparent;
            color: #17191D;
            font-size: 14px;
        }


        /* =================================================
           MITRA BUBBLE
        ================================================= */

        #mitraBubble {
            background-color: #181B21;
            border: 1px solid #292E38;
            border-radius: 18px;
        }

        #mitraBubbleText {
            background-color: transparent;
            color: #F2F3F5;
            font-size: 14px;
        }


        /* =================================================
           INPUT
        ================================================= */

        #inputFrame {
            background-color: #171A20;
            border: 1px solid #2A2F38;
            border-radius: 18px;
        }

        #messageInput {
            background-color: transparent;
            border: none;
            padding: 10px 14px;
            color: #F3F4F6;
            font-size: 14px;
        }

        #messageInput:focus {
            border: none;
        }

        #messageInput::placeholder {
            color: #626975;
        }


        /* =================================================
           MICROPHONE BUTTON
        ================================================= */

        #micButton {
            background-color: #242932;
            color: #F0F1F3;
            border: none;
            border-radius: 14px;
            font-size: 19px;
        }

        #micButton:hover {
            background-color: #303640;
        }

        #micButton:pressed {
            background-color: #3A404B;
        }

        #micButton:disabled {
            background-color: #191C22;
            color: #555B65;
        }


        /* =================================================
           SEND BUTTON
        ================================================= */

        #sendButton {
            background-color: #F0F1F3;
            color: #111318;
            border: none;
            border-radius: 14px;
            font-size: 20px;
            font-weight: bold;
        }

        #sendButton:hover {
            background-color: #FFFFFF;
        }

        #sendButton:pressed {
            background-color: #D4D6DA;
        }

        #sendButton:disabled {
            background-color: #40444C;
            color: #777C85;
        }


        /* =================================================
           SCROLLBAR
        ================================================= */

        QScrollBar:vertical {
            background-color: transparent;
            width: 8px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background-color: #303640;
            border-radius: 4px;
            min-height: 40px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #424955;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }

        """)


# =========================================================
# APPLICATION
# =========================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = MitraWindow()

    window.show()

    sys.exit(
        app.exec()
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()