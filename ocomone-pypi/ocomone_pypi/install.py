import os

from passlib.hash import pbkdf2_sha256

DEFAULT_PORT = 62220
DEFAULT_DIR = "/opt/pypi/packages/"
HTPASSWD_FILE = ".htpasswd"


def _save_passwd(username, password, file_path):
    with open(file_path, "w+") as file:
        auth_str = f"{username}:{pbkdf2_sha256.hash(password)}"
        file.write(auth_str)


CONFIG_FILE_NAME = ".config"


def get_config_file():
    """Return path to config file"""
    return os.path.abspath(get_config_path() + "/" + CONFIG_FILE_NAME)


def _save_cmd(command):
    with open(get_config_file(), "w+") as file:
        file.write(command)


def get_config_path():
    """Return path to server configuration for current user"""
    return os.path.abspath(os.path.expanduser("~") + "/.pypi-server")


PID_FILE_NAME = "pypi.pid"


def get_pid_file():
    """Return PID file for server running for current user"""
    return os.path.abspath(get_config_path() + "/" + PID_FILE_NAME)


def main():
    """Interactive installation"""
    config_path = get_config_path()
    os.makedirs(config_path, mode=0o700, exist_ok=True)

    server_port = input(f"PyPi port [{DEFAULT_PORT}]: ") or DEFAULT_PORT
    username = input("Enter uploader username: ")
    password = input("Enter uploader password: ")
    read_too = input("Restrict download access? [n]: ") or "n"
    rights = "update,download" if read_too.lower() == "y" else "update"
    download_dir = input(f"Directory for file download [{DEFAULT_DIR}]: ") or DEFAULT_DIR

    _save_passwd(username, password, f"{config_path}/{HTPASSWD_FILE}")

    command = (
        "start-stop-daemon "
        f"-bd {config_path} "
        f"-S -mp {PID_FILE_NAME} "
        "--exec /usr/local/bin/poetry "
        "-- run pypi-server "
        f"--port {server_port} "
        f"-P {HTPASSWD_FILE} "
        f"-a {rights} {download_dir}"
    )
    _save_cmd(command)



if __name__ == '__main__':
    # subprocess.call("python3 -m pip install poetry", shell=True)
    main()
