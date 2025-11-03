from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QToolBar,
    QAction,
    QTabWidget,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QEvent
import sys
import datetime


class BlindWriter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Écriture sans retour")
        self.resize(600, 400)

        self.last_text = ""

        self.filename = f"ecriture_{datetime.date.today()}.txt"

        self.create_toolbox()

        self.setCentralWidget(self.init_ui())

    def create_toolbox(self):
        toolbar = QToolBar("Outils", self)
        self.addToolBar(toolbar)

        save_action = QAction("Enregistrer", self)
        save_action.setStatusTip("Enregistrer le texte actuel")
        save_action.triggered.connect(self.save_textbox_content)
        toolbar.addAction(save_action)

        close_action = QAction("Fermer", self)
        close_action.setStatusTip("Fermer l'application")
        close_action.triggered.connect(self.close)
        toolbar.addAction(close_action)

    def init_ui(self) -> QWidget:
        widget = QWidget()

        layout = QVBoxLayout()

        layout.addWidget(self.main_menu_widget())

        self.textbox = QTextEdit()
        self.textbox.setPlaceholderText("Commence à écrire ici...")
        self.textbox.setFont(QFont("Times New Roman", 16))
        self.textbox.installEventFilter(self)

        layout.addWidget(self.textbox)

        widget.setLayout(layout)

        return widget

    def main_menu_widget(self) -> QTabWidget:
        tab_widget = QTabWidget()

        tab_widget.addTab(QWidget(), "Écriture")
        tab_widget.addTab(QWidget(), "Paramètres")
        tab_widget.addTab(QWidget(), "Aide")

        return tab_widget

    def eventFilter(self, source, event):
        if source == self.textbox and event.type() == QEvent.KeyPress:
            key = event.key()
            text = self.textbox.toPlainText().strip()
            if text:
                if key == Qt.Key_Space and text[-1] in [
                    ".",
                    "?",
                    "!",
                ]:
                    self.save_and_clear()
                    return True
        return super().eventFilter(source, event)

    def save_and_clear(self):
        text = self.textbox.toPlainText().strip()
        if text:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(text)
            self.textbox.clear()

    def save_textbox_content(self):
        self.save_and_clear()
        QMessageBox.information(self, "Enregistré", "Le texte a été enregistré.")

    def onKeyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlindWriter()
    window.showMaximized()
    sys.exit(app.exec())
