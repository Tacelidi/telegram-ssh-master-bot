import socket
import asyncssh
from asyncssh import SSHClientConnection
from paramiko.ssh_exception import AuthenticationException, SSHException
from dataclasses import dataclass


def _handle_ssh_error(error: Exception) -> str:
    match error:
        case AuthenticationException():
            return "Ошибка аутентификации. Проверьте пароль и имя пользователя."

        case socket.timeout | TimeoutError():
            return "Таймаут соединения. Проверьте адрес и доступность соединения"

        case socket.gaierror():
            return "Хост не найден. Проверьте правильность адреса"

        case ConnectionRefusedError():
            return "Сервер отказал в подключении. SSH может быть отключен или слушает другой порт"

        case ConnectionResetError():
            return "Соединение было разорвано"

        case EOFError():
            return "Неожиданный разрыв соединения с сервером"

        case SSHException():
            return f"Ошибка SSH: {str(error)}"

        case _:
            return f"Непредвиденная ошибка: {type(error).__name__}:{str(error)}"


@dataclass
class SSHFullData:
    username: str
    password: str
    address: str

    async def _get_connection(self) -> SSHClientConnection:
        return await asyncssh.connect(
            self.address, user=self.username, password=self.password, timeout=10
        )

    async def _run_command(self, command: str) -> str:
        try:
            async with await self._get_connection() as conn:
                result = await conn.run(command, check=False)

                if result.exit_status == 0:
                    return (result.stdout or "Команда выполнена").strip()

                output = (result.stderr or result.stdout or "").strip()
                if output:
                    return f"Команда завершилась с ошибкой:\n{output}"
                return f"Команда завершилась с кодом {result.exit_status}"

        except Exception as e:
            return _handle_ssh_error(e)

    async def restart(self) -> str:
        return await self._run_command("sudo reboot")

    async def shutdown(self) -> str:
        return await self._run_command("sudo shutdown -h now")

    async def send_command(self, command: str) -> str:
        return await self._run_command(command)
