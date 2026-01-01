import socket
from fabric import Connection
from invoke.exceptions import UnexpectedExit
from paramiko.ssh_exception import AuthenticationException, SSHException
from dataclasses import dataclass


def _handle_ssh_error(error: Exception) -> str:
    match error:
        case AuthenticationException(): return "Ошибка аутентификации. Проверьте пароль и имя пользователя."

        case socket.timeout: return "Таймаут соединения. Проверьте адрес и доступность соединения"

        case socket.gaierror(): return "Хост не найден. Проверьте правильность адреса"

        case ConnectionRefusedError(): return "Сервер отказал в подключении. SSH может быть отключен или слушает другой порт"

        case ConnectionResetError(): return "Соединение было разорвано"

        case EOFError(): return "Неожиданный разрыв соединения с сервером"

        case SSHException(): return f"Ошибка SSH: {str(error)}"

        case UnexpectedExit() as e:
            output = (e.result.stderr or e.result.stdout or "").strip()
            if output:
                return f"Команда завершилась с ошибкой:\n{output}"
            return f"Команда завершилась с кодом ошибки {e.result.return_code}"

        case _:
            return f"Непредвиденная ошибка: {type(error).__name__}:{str(error)}"

@dataclass
class SSHFullData:
    username: str
    password: str
    address: str

    def _get_connection(self) -> Connection:
        return Connection(
            self.address, user=self.username, connect_kwargs={"password": self.password, "timeout": 10}
        )

    def _run_sudo(self, command: str) -> str:
        try:
            with self._get_connection() as conn:
                result = conn.sudo(command, hide=True)
                return (result.stdout or "Команда выполнена").strip()
        except Exception as e:
            return _handle_ssh_error(e)

    def restart(self) -> str:
        return self._run_sudo("reboot")

    def shutdown(self) -> str:
        return self._run_sudo("shutdown -h now")

    def send_command(self, command: str) -> str:
        return self._run_sudo(command)
