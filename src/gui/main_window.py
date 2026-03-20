from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QCheckBox, QPushButton,
    QLineEdit, QGroupBox, QRadioButton, QListWidgetItem,QMessageBox, QProgressBar
)
from src.service.utils.cd_writer import write_json_to_cd
from src.service.utils.windows_programs import get_installed_programs
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt, QTimer, Signal, QObject
import os
import json
import threading

class WorkerSignals(QObject):
    finished = Signal(bool, str)

class MainWindow(QMainWindow):
    # todo precisa garantir que vai pegar o exe do jogo quando ele tem icone
    # atualmente se o jogo tem icone o json salva o path para o .ico ao invés do .exe

    def __init__(self):
        super().__init__()

        self.signals = WorkerSignals()
        self.signals.finished.connect(self.finish_generate_json)

        self.default_icon = QIcon("src/assets/CD_Icon.png")
        self.setWindowTitle("CD Launcher")
        QTimer.singleShot(0, self.showMaximized)

        main_layout = QVBoxLayout()

        # ==============================
        # SEGMENTO 1 - JOGOS
        # ==============================

        games_box = QGroupBox("Selecionar programa")

        games_layout = QVBoxLayout()

        # campo de busca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar programa...")

        # lista de programas
        self.games_list = QListWidget()
        self.games_list.setIconSize(QSize(16, 16))

        games_layout.addWidget(self.search_bar)
        games_layout.addWidget(self.games_list)

        games_box.setLayout(games_layout)
        self.programs = get_installed_programs()
        self.populate_program_list(self.programs)
        self.filtered_programs = self.programs.copy()
        self.search_bar.textChanged.connect(self.filter_programs)

        # ==============================
        # SEGMENTO 2 - CONFIG TELA
        # ==============================

        screen_box = QGroupBox("Configurações de execução")

        screen_layout = QVBoxLayout()

        self.big_picture_checkbox = QCheckBox("Abrir Steam Big Picture")

        screen_layout.addWidget(self.big_picture_checkbox)

        screen_layout.addWidget(QLabel("Modo de exibição"))

        self.display_primary = QRadioButton("Tela principal")
        self.display_second = QRadioButton("Segunda tela somente")
        self.display_extend = QRadioButton("Estender")
        self.display_duplicate = QRadioButton("Duplicar")

        self.display_primary.setChecked(True)

        screen_layout.addWidget(self.display_primary)
        screen_layout.addWidget(self.display_second)
        screen_layout.addWidget(self.display_extend)
        screen_layout.addWidget(self.display_duplicate)

        screen_box.setLayout(screen_layout)

        # ==============================
        # SEGMENTO 3 - WEB
        # ==============================

        web_box = QGroupBox("Abrir página web")

        web_layout = QVBoxLayout()

        self.web_checkbox = QCheckBox("Abrir website ao invés de programa")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://")

        web_layout.addWidget(self.web_checkbox)
        web_layout.addWidget(self.url_input)

        web_box.setLayout(web_layout)

        # ==============================
        # SEGMENTO 4 - AÇÕES
        # ==============================

        bottom_box = QGroupBox()

        bottom_layout = QHBoxLayout()

        # estado interno do serviço
        self.service_active = False

        # botão ativar / desativar
        self.service_button = QPushButton()
        self.service_button.setMinimumHeight(40)
        self.service_button.clicked.connect(self.toggle_service)

        # texto de status
        self.service_status = QLabel()
        self.service_status.setStyleSheet("font-size:16px;")

        # botão gerar JSON
        self.generate_button = QPushButton("Gravar CD")
        self.generate_button.setMinimumHeight(50)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # isso deixa infinito (loading)
        self.progress_bar.setVisible(False)


        # adicionar elementos
        bottom_layout.addWidget(self.service_button)
        bottom_layout.addWidget(self.service_status)

        bottom_layout.addStretch()

        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addWidget(self.generate_button)

        bottom_box.setLayout(bottom_layout)

        # atualizar estado inicial
        self.update_service_ui()

        # ==============================
        # ADD NA PAGINA
        # ==============================

        main_layout.addWidget(games_box)
        main_layout.addWidget(screen_box)
        main_layout.addWidget(web_box)
        main_layout.addStretch()
        main_layout.addWidget(bottom_box)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.generate_button.clicked.connect(self.start_generate_json)


    def toggle_service(self):
        self.service_active = not self.service_active
        self.update_service_ui()

    def update_service_ui(self):
        if self.service_active:
            self.service_button.setText("Desativar")
            self.service_status.setText("observando CD")
            print("Serviço ATIVADO")
        else:
            self.service_button.setText("Ativar")
            self.service_status.setText("modo de configuração")
            print("Serviço DESATIVADO")
    
    def populate_program_list(self, programs):
        self.games_list.clear()
        self.filtered_programs = programs
        for program in programs:
            item = QListWidgetItem(program["name"])
            icon = None
            if ".ico" in program["icon"] and os.path.exists(program["icon"]):
                print(program['icon'])
                icon = QIcon(program["icon"])
            if not icon or icon.isNull():
                icon = self.default_icon
            item.setIcon(icon)
            self.games_list.addItem(item)

    def filter_programs(self, text):
        text = text.lower() 
        filtered = [
            p for p in self.programs
            if text in p["name"].lower()
        ]
        self.populate_program_list(filtered)

    def start_generate_json(self):
        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        threading.Thread(target=self.generate_json, daemon=True).start()    

    def generate_json(self):
        selected_row = self.games_list.currentRow()
        if selected_row < 0:
            print("Nenhum programa selecionado")
            return

        program = self.filtered_programs[selected_row]
        exe_path = program["exe"]

        display_mode = "primary"
        if self.display_second.isChecked():
            display_mode = "second_screen"
        elif self.display_extend.isChecked():
            display_mode = "extend"
        elif self.display_duplicate.isChecked():
            display_mode = "duplicate"

        big_picture = self.big_picture_checkbox.isChecked()

        open_web = self.web_checkbox.isChecked()
        url = self.url_input.text()

        if open_web:
            data = {
                "action": "open_web",
                "url": url,
                "display_mode": display_mode
            }
        else:
            data = {
                "action": "launch_program",
                "exe": exe_path,
                "display_mode": display_mode,
                "big_picture": big_picture
            }

        json_path = "launch.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        # 🔥 GRAVA CD
        success, message = write_json_to_cd(json_path)

        # 🔥 FECHAR EXPLORER DO CD
        if success:
            import subprocess
            import time

            time.sleep(1)

            subprocess.run([
                "powershell",
                "-Command",
                """
                $shell = New-Object -ComObject Shell.Application
                $windows = $shell.Windows()
                foreach ($w in $windows) {
                    if ($w.LocationURL -like "*CD*") {
                        $w.Quit()
                    }
                }
                """
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 🔥 VOLTA PRA UI
        self.signals.finished.emit(success, message)

    def finish_generate_json(self, success, message):
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)

        if success:
            QMessageBox.information(
                self,
                "CD gravado",
                "O JSON foi gravado no CD com sucesso!"
            )
        else:
            QMessageBox.critical(
                self,
                "Erro ao gravar CD",
                message
            )