from fabric import Connection
from invoke.exceptions import UnexpectedExit
from paramiko.ssh_exception import AuthenticationException


class SSHFullData:
    def __init__(self, username, password, address):
        self.address = address
        self.username = username
        self.password = password

    def _get_connection(self):
        return Connection(self.address, user=self.username, connect_kwargs={'password': self.password})

    def _run_sudo(self, command):
        try:
            with self._get_connection() as conn:
                result = conn.sudo(command, hide=True)
                return (result.stdout or "Команда выполнена").strip()
        except AuthenticationException as e:
            return f"Ошибка аунтефикации по SSH: {e}"
        except UnexpectedExit as e:
            out = (e.result.stderr or e.result.stdout or "").strip()
            if out:
                return f"Комманда завершилась с ошибкой:\n{out}"
            return "Комманда звершилась с неудачным кодом"
        except Exception as e:
            return f"Не удалось выполнить комманду: {e}"

    def restart(self):
        return self._run_sudo("reboot")

    def shutdown(self):
        return self._run_sudo("shutdown -h now")

    def send_command(self, command):
        return self._run_sudo(command)
