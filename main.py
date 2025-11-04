from configparser import RawConfigParser
import os
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QToolBar,
    QLabel,
    QMenuBar,
    QMenu,
    QAction,
    QTabWidget,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QEvent
import sys
import datetime


class BlindWriter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Écriture sans retour")
        self.resize(600, 400)

        self.file_path = None
        self.init_config_file()

        self.last_text = ""

        self.create_menu_bar()
        self.create_toolbox()

        self.setCentralWidget(self.init_ui())

    def create_menu_bar(self) -> None:
        new_file_action = QAction("Nouveau", self)
        new_file_action.setStatusTip("Créer un nouveau un fichier texte")
        new_icon = self.style().standardIcon(QApplication.style().SP_FileIcon)
        new_file_action.setIcon(new_icon)
        new_file_action.setShortcut("Ctrl+N")
        new_file_action.triggered.connect(self.create_new_file)

        open_file_action = QAction("Ouvrir", self)
        open_file_action.setStatusTip("Ouvrir un fichier texte")
        open_file_action.setIcon(
            self.style().standardIcon(QApplication.style().SP_DialogOpenButton)
        )
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file)

        save_action = QAction("Enregistrer", self)
        save_action.setStatusTip("Enregistrer")
        save_action.setIcon(
            self.style().standardIcon(QApplication.style().SP_DialogSaveButton)
        )
        save_action.triggered.connect(self.save)
        save_action.setShortcut("Ctrl+S")

        down_save_action = QAction("Enregistrer-sous", self)
        down_save_action.setStatusTip("Enregistrer-sous")
        down_save_action.setIcon(
            self.style().standardIcon(QApplication.style().SP_DialogSaveButton)
        )
        down_save_action.triggered.connect(self.down_save)
        down_save_action.setShortcut("Ctrl+Shift+S")

        close_action = QAction("Fermer", self)
        close_action.setStatusTip("Fermer l'application")
        close_icon = self.style().standardIcon(
            QApplication.style().SP_DialogCloseButton
        )
        close_action.setIcon(close_icon)
        close_action.triggered.connect(self.close)
        close_action.setShortcut("Ctrl+Q")

        folder_menu = QMenu("Fichier", self)
        folder_menu.setStatusTip("Enregistrez le texte actuel")
        folder_menu.addAction(new_file_action)
        folder_menu.addAction(open_file_action)
        folder_menu.addAction(save_action)
        folder_menu.addAction(down_save_action)
        folder_menu.addAction(close_action)

        mode_menu = QMenu("Modes", self)
        mode_menu.setStatusTip("Choisissez parmi les différents modes")

        menubar = QMenuBar(self)
        menubar.addMenu(folder_menu)
        menubar.addMenu(mode_menu)

        self.setMenuBar(menubar)

    def create_new_file(self) -> None:
        if self.checks_current_file():
            self.file_path = ""
            self.file_name_label.setText("Document non-enregistré   ")

    def reset_textbox(self) -> None:
        self.textbox.setHidden(False)
        self.textbox.clear()

    def open_file(self):
        if self.checks_current_file():
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier texte",
                self.config.get("recent_file", "open_file_path"),
                "Fichiers texte (*.txt);;Tous les fichiers (*)",
            )
            if file_path:
                self.file_path = file_path
                try:

                    file_path_splitted = file_path.split("/")
                    file_name = file_path_splitted[-1]
                    self.file_name_label.setText(file_name)
                    self.file_path = file_path
                    self.file_name_label.setText(file_name)
                    self.textbox.setHidden(False)
                    self.complete_text_box()

                    self.config.set(
                        "recent_file",
                        "open_file_path",
                        "/".join(file_path_splitted[:-1]),
                    )
                    self.write_config_file()

                    self.config.set("recent_file", "name", file_path)
                    with open(
                        "main_config.properties", "w", encoding="utf-8"
                    ) as configfile:
                        self.config.write(configfile)

                except Exception as e:
                    QMessageBox.warning(
                        self, "Erreur", f"Impossible d'ouvrir le fichier :\n{e}"
                    )

    def checks_current_file(self) -> None:
        text = self.textbox.toPlainText()
        if self.init_text != text:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Attention")
            msg_box.setText(
                "Le texte courant va être supprimé. Voulez-vous enregistrer avant ?"
            )
            msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            # Personnalisation des boutons en français
            save_button = msg_box.button(QMessageBox.Save)
            if save_button:
                save_button.setText("Enregistrer")
            discard_button = msg_box.button(QMessageBox.Discard)
            if discard_button:
                discard_button.setText("Ne pas enregistrer")
            cancel_button = msg_box.button(QMessageBox.Cancel)
            if cancel_button:
                cancel_button.setText("Annuler")

            ret = msg_box.exec_()
            if ret == QMessageBox.Save:
                self.save_and_clear()
                self.reset_textbox()
                return True
            elif ret == QMessageBox.Cancel:
                return False
            elif ret == QMessageBox.Discard:
                self.reset_textbox()
                return True
        else:
            if len(text) >= 1:
                self.reset_textbox()

            return True

    def init_config_file(self) -> None:
        FILE_NAME = "main_config.properties"
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                pass

        self.config = RawConfigParser()
        self.config.read(FILE_NAME)

        if not self.config.has_section("recent_file"):
            self.config.add_section("recent_file")

        if not self.config.has_option("recent_file", "name"):
            self.config.set("recent_file", "name", "")
        else:
            self.file_path = self.config.get("recent_file", "name")

        if not self.config.has_option("recent_file", "open_file_path"):
            self.config.set("recent_file", "open_file_path", "")

        if not self.config.has_option("recent_file", "save_file_path"):
            self.config.set("recent_file", "save_file_path", "")

        self.write_config_file()

    def create_toolbox(self):
        # toolbar = QToolBar("Outils", self)
        # self.addToolBar(toolbar)

        # save_action = QAction("Enregistrer", self)
        # save_action.setStatusTip("Enregistrer le texte actuel")
        # # Ajout d'une icône standard pour l'action enregistrer
        # save_action.setIcon(
        #     self.style().standardIcon(QApplication.style().SP_DialogSaveButton)
        # )
        # save_action.triggered.connect(self.save)
        # toolbar.addAction(save_action)
        pass

    def init_ui(self) -> QWidget:
        widget = QWidget()

        layout = QVBoxLayout()

        layout.addWidget(self.main_menu_widget())

        self.file_name_label = QLabel()
        layout.addWidget(self.file_name_label)

        self.textbox = QTextEdit()
        self.textbox.setFont(QFont("Times New Roman", 16))
        self.textbox.installEventFilter(self)
        self.textbox.setAcceptRichText(False)

        if self.file_path:
            self.complete_text_box()
        else:
            self.textbox.setHidden(True)

        layout.addWidget(self.textbox)

        widget.setLayout(layout)

        return widget

    def complete_text_box(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content:
                    self.textbox.setText(content)
                    file_path_splitted = self.file_path.split("/")
                    file_name = file_path_splitted[-1]
                    self.file_name_label.setText(file_name)
                    self.init_text = content
                else:
                    self.textbox.clear()
        else:
            print("Le fichier a été déplacé ou supprimé...")
            self.config.set("recent_file", "name", "")
            self.write_config_file()
            self.textbox.setHidden(True)

    def write_config_file(self) -> None:
        FILE_NAME = "main_config.properties"
        try:
            with open(FILE_NAME, "w", encoding="utf-8") as configfile:
                self.config.write(configfile)
        except FileNotFoundError as fnfe:
            print(f"Le fichier {FILE_NAME} n'a pas été trouvé. {fnfe}")

    def main_menu_widget(self) -> QTabWidget:
        tab_widget = QTabWidget()

        tab_widget.addTab(QWidget(), "Écriture")
        tab_widget.addTab(QWidget(), "Paramètres")
        tab_widget.addTab(QWidget(), "Aide")

        tab_widget.setFixedHeight(200)

        return tab_widget

    def eventFilter(self, source, event):
        if source == self.textbox and event.type() == QEvent.KeyPress:
            key = event.key()
            text = self.textbox.toPlainText().strip()
            if text:
                if (
                    key == Qt.Key_Space
                    and text[-1]
                    in [
                        ".",
                        "?",
                        "!",
                    ]
                    or key == Qt.Key_Return
                ):
                    self.save_and_clear()
                    return True
        return super().eventFilter(source, event)

    def save_and_clear(self):
        self.save()

        if self.file_path:
            self.textbox.clear()

    def save(self) -> None:
        if self.textbox.isVisible():
            if self.file_path:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(self.textbox.toPlainText().strip())

                self.update_recent_file_name()
            else:
                self.down_save()

    def down_save(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le fichier texte",
            self.config.get("recent_file", "save_file_path"),
        )
        if file_path:
            file_path += ".txt"
            self.update_recent_save_path(file_path)
            self.update_recent_file_name(file_path)

            with open(self.file_path, "w") as f:
                f.write(self.textbox.toPlainText().strip())

            QMessageBox.information(
                self,
                "Enregistrement réussi",
                f"Le fichier a été enregistré sous :\n{self.file_path}\n\nRépertoire : {self.config.get('recent_file', 'save_file_path')}",
            )
        else:
            QMessageBox.warning(
                self,
                "Enregistrement non-effectué",
                "Veuillez sélectionner un dossier",
            )

    def update_recent_save_path(self, file_path: str) -> None:
        file_path_splitted = file_path.split("/")
        file_name = file_path_splitted[-1]
        self.file_name_label.setText(file_name)
        self.file_path = file_path

        self.config.set(
            "recent_file", "save_file_path", "/".join(file_path_splitted[:-1])
        )
        self.write_config_file()

    def update_recent_file_name(self) -> None:
        self.config.set("recent_file", "name", self.file_path)
        self.write_config_file()

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
