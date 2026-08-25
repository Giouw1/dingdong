import sys
import requests
from requests.auth import HTTPBasicAuth
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QListWidget, 
    QSpinBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt

class AuthWidget(QWidget):
    """Widget responsável pela Autenticação do usuário (Login/Registro)."""
    def __init__(self, parent_controller) -> None:
        super().__init__()
        self.controller = parent_controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Login")
        self.register_btn = QPushButton("Registrar")

        self.login_btn.clicked.connect(self._on_login_clicked)
        self.register_btn.clicked.connect(self._on_register_clicked)

        layout.addWidget(QLabel("Autenticação do Sistema"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)

    def _on_login_clicked(self) -> None:
        self.controller.execute_login(
            self.username_input.text(), 
            self.password_input.text()
        )

    def _on_register_clicked(self) -> None:
        self.controller.execute_register(
            self.username_input.text(), 
            self.password_input.text()
        )


class DashboardWidget(QWidget):
    """Widget responsável pelas operações pós-autenticação."""
    def __init__(self, parent_controller) -> None:
        super().__init__()
        self.controller = parent_controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        # -----------------------------------------------------
        # Seção 1: Identidade (Nickname)
        # -----------------------------------------------------
        identity_group = QGroupBox("Identidade")
        identity_layout = QVBoxLayout()
        
        self.nickname_display = QLabel("Nickname: Não definido")
        self.nickname_display.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        nickname_edit_layout = QHBoxLayout()
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("Novo Nickname")
        
        self.change_nick_btn = QPushButton("Alterar Nickname")
        self.change_nick_btn.clicked.connect(self._on_change_nick_clicked)
        
        nickname_edit_layout.addWidget(self.nickname_input)
        nickname_edit_layout.addWidget(self.change_nick_btn)
        
        identity_layout.addWidget(self.nickname_display)
        identity_layout.addLayout(nickname_edit_layout)
        identity_group.setLayout(identity_layout)

        # -----------------------------------------------------
        # Seção 2: Notificações
        # -----------------------------------------------------
        control_group = QGroupBox("Caixa Postal")
        control_layout = QHBoxLayout()
        
        self.offset_spinbox = QSpinBox()
        self.offset_spinbox.setMinimum(0)
        self.offset_spinbox.setPrefix("Offset: ")
        
        self.amount_spinbox = QSpinBox()
        self.amount_spinbox.setMinimum(1)
        self.amount_spinbox.setValue(5)
        self.amount_spinbox.setPrefix("Amount: ")
        
        self.fetch_btn = QPushButton("Buscar")
        self.fetch_btn.clicked.connect(self._on_fetch_clicked)

        control_layout.addWidget(self.offset_spinbox)
        control_layout.addWidget(self.amount_spinbox)
        control_layout.addWidget(self.fetch_btn)
        
        self.notification_list = QListWidget()
        
        control_vlayout = QVBoxLayout()
        control_vlayout.addLayout(control_layout)
        control_vlayout.addWidget(self.notification_list)
        control_group.setLayout(control_vlayout)

        # -----------------------------------------------------
        # Seção 3: Logout
        # -----------------------------------------------------
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.controller.execute_logout)

        layout.addWidget(identity_group)
        layout.addWidget(control_group)
        layout.addWidget(self.logout_btn)
        
        self.setLayout(layout)

    def set_nickname_display(self, nickname: str) -> None:
        self.nickname_display.setText(f"Nickname atual: {nickname}")
        self.nickname_input.clear()

    def update_notifications(self, data: list) -> None:
        self.notification_list.clear()
        if not data:
            self.notification_list.addItem("Nenhuma notificação encontrada.")
            return
        for item in data:
            self.notification_list.addItem(str(item))

    def _on_change_nick_clicked(self) -> None:
        new_nick = self.nickname_input.text().strip()
        if new_nick:
            self.controller.execute_change_nickname(new_nick)
            
    def _on_fetch_clicked(self) -> None:
        self.controller.execute_fetch_notifications(
            self.amount_spinbox.value(), 
            self.offset_spinbox.value()
        )


class MainWindow(QMainWindow):
    """Controlador que orquestra os estados e a interface de rede."""
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Cliente API Mailbox")
        self.resize(500, 600)
        
        # Objeto Session gerencia automaticamente o cookie 'session_id' injetado pelo gateway
        self.api_session = requests.Session()
        self.base_url = "http://127.0.0.1:8000/owner" # Ajuste conforme host/porta do servidor
        
        self.current_nickname: str | None = None

        self.stacked_widget = QStackedWidget()
        self.auth_view = AuthWidget(self)
        self.dashboard_view = DashboardWidget(self)

        self.stacked_widget.addWidget(self.auth_view)
        self.stacked_widget.addWidget(self.dashboard_view)

        self.setCentralWidget(self.stacked_widget)

    def execute_login(self, username, password) -> None:
        try:
            response = self.api_session.post(
                f"{self.base_url}/login",
                auth=HTTPBasicAuth(username, password)
            )
            
            if response.status_code == 200:
                self.current_nickname = response.json()
                self.dashboard_view.set_nickname_display(self.current_nickname)
                self.stacked_widget.setCurrentWidget(self.dashboard_view)
            else:
                QMessageBox.warning(self, "Falha de Autenticação", f"Erro: {response.text}")
                
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")

    def execute_register(self, username, password) -> None:
        try:
            response = self.api_session.post(
                f"{self.base_url}/register",
                auth=HTTPBasicAuth(username, password)
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Sucesso", "Usuário registrado com sucesso. Efetue o login.")
            else:
                QMessageBox.warning(self, "Falha no Registro", f"Erro: {response.text}")
                
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")

    def execute_change_nickname(self, new_nickname: str) -> None:
        try:
            response = self.api_session.post(
                f"{self.base_url}/nickname/change",
                params={"Nickname": new_nickname}
            )
            
            if response.status_code == 200:
                self.current_nickname = new_nickname
                self.dashboard_view.set_nickname_display(self.current_nickname)
                QMessageBox.information(self, "Sucesso", "Nickname atualizado.")
            else:
                QMessageBox.warning(self, "Erro", f"Não foi possível atualizar o nickname: {response.text}")
                
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Falha na requisição: {e}")

    def execute_fetch_notifications(self, amount: int, offset: int) -> None:
        try:
            response = self.api_session.get(
                f"{self.base_url}/notifications",
                params={"msg_amount": amount, "offset": offset}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.dashboard_view.update_notifications(data)
            elif response.status_code == 401:
                QMessageBox.warning(self, "Sessão Expirada", "Realize o login novamente.")
                self.execute_logout()
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar notificações: {response.text}")
                
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Falha na requisição: {e}")

    def execute_logout(self) -> None:
        try:
            self.api_session.post(f"{self.base_url}/logout")
        except requests.RequestException:
            pass # Ignora falhas de rede no logout; a limpeza local deve prosseguir incondicionalmente
            
        self.api_session.cookies.clear()
        self.current_nickname = None
        
        self.dashboard_view.notification_list.clear()
        self.auth_view.username_input.clear()
        self.auth_view.password_input.clear()
        
        self.stacked_widget.setCurrentWidget(self.auth_view)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()