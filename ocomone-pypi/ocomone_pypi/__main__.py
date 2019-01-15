"""Micro pypi server"""
import argparse
import subprocess

from ocomone_pypi import install


def _main():
    argp = argparse.ArgumentParser(description="Micro pypi server")
    argp.add_argument("--install", action="store_true", default=False, help="Start new interactive installation")
    argp.add_argument("--start", action="store_true", default=False, help="Start server")
    argp.add_argument("--stop", action="store_true", default=False, help="Stop server")
    args = argp.parse_args()
    if args.install:
        install.main()
    if args.start:
        script_file = install.get_config_file()
        subprocess.call(["/bin/sh", script_file], shell=True)
    if args.stop:
        subprocess.call(["start-stop-daemon", "-Kp", install.get_pid_file()])


if __name__ == '__main__':
    _main()
