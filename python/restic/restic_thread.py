import json
import os
import sys
import shutil
import signal
import logging
import pyotherside
from subprocess import Popen, PIPE
import sfsecret


logger = logging.getLogger("restatic")


class ResticThread():
    """
    Base class to run `restic` command line jobs. If a command needs more pre- or post-processing
    it should sublass `ResticThread`.
    """

    def __init__(self, cmd, params, parent=None):
        """
        Thread to run Restic operations in.

        :param cmd: Restic command line
        :param params: Pass options that were used to build cmd and may be needed to
                       process the result.
        :param parent: Parent window. Needs `thread.wait()` if none. (scheduler)
        """
        cmd[0] = self.prepare_bin()

        env = os.environ.copy()
        env["RESTIC_HOSTNAME_IS_UNIQUE"] = "1"
        if params.get("password") and params["password"] is not None:
            env["RESTIC_PASSWORD"] = params["password"]

        env["RESTIC_RSH"] = "ssh -oStrictHostKeyChecking=no"
        if params.get("ssh_key") and params["ssh_key"] is not None:
            env["RESTIC_RSH"] += f' -i ~/.ssh/{params["ssh_key"]}'

        self.env = env
        self.cmd = cmd
        self.params = params
        self.process = None

    @classmethod
    def prepare(cls, profile):
        """
        Prepare for running Restic. This function in the base class should be called from all
        subclasses and calls that define their own `cmd`.

        The `prepare()` step does these things:
        - validate if all conditions to run command are met
        - build restic command

        `prepare()` is run 2x. First at the global level and then for each subcommand.

        :return: dict(ok: book, message: str)
        """
        ret = {"ok": False}

        if cls.prepare_bin() is None:
            ret["message"] = "Restic binary was not found."
            return ret

        if profile.repo is None:
            ret["message"] = "Add a backup repository first."
            return ret

        ret["ssh_key"] = profile.ssh_key
        ret["repo_id"] = profile.repo.id
        ret["backup_destination"] = profile.repo.url
        ret["profile_name"] = profile.name
        ret["password"] = sfsecret.get_secret("restic", "password")
        ret["ok"] = True

        return ret

    @classmethod
    def prepare_bin(cls):
        """Find packaged restic binary. Prefer globally installed."""
        # Look in current PATH.
        if shutil.which("restic"):
            return "restic"

    def run(self):
        self.started_event()
        self.process = Popen(
            self.cmd,
            stdout=PIPE,
            stderr=PIPE,
            bufsize=1,
            universal_newlines=True,
            env=self.env,
            preexec_fn=os.setsid,
        )

        for line in iter(self.process.stderr.readline, ""):
            try:
                self.process_line(line)  # hook for lines
                parsed = json.loads(line)
                if parsed["type"] == "log_message":
                    self.log_event(f'{parsed["levelname"]}: {parsed["message"]}')
                    level_int = getattr(logging, parsed["levelname"])
                    logger.log(level_int, parsed["message"])
                elif parsed["type"] == "file_status":
                    self.log_event(f'{parsed["path"]} ({parsed["status"]})')
            except json.decoder.JSONDecodeError:
                msg = line.strip()
                self.log_event(msg)
                logger.warning(msg)

        self.process.wait()
        stdout = self.process.stdout.read()
        result = {
            "params": self.params,
            "returncode": self.process.returncode,
            "cmd": self.cmd,
        }
        try:
            result["data"] = json.loads(stdout)
        except:  # noqa
            result["data"] = {}

        self.process_result(result)
        self.finished_event(result)

    def cancel(self):
        if self.isRunning():
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.terminate()

    def process_line(self, line):
        pyotherside.send('line', line)

    def process_result(self, result):
        pyotherside.send('result', result)

    def log_event(self, msg):
        pyotherside.send('updated', msg)

    def started_event(self):
        pyotherside.send('info', "Task started")

    def finished_event(self, result):
        pyotherside.send('finished', result)


class ResticThreadChain(ResticThread):
    """
    Metaclass of `ResticThread` that can run multiple other ResticThread actions while providing the same
    interface as a single action.
    """

    def __init__(self, cmds, input_values, parent=None):
        """
        Takes a list of tuples with `ResticThread` subclass and optional input parameters. Then all actions are executed
        and a merged result object is returned to the caller. If there is any error, then current result is returned.

        :param actions:
        :return: dict(results)
        """
        self.parent = parent
        self.threads = []
        self.combined_result = {}

        for cmd, input_value in zip(cmds, input_values):
            if input_value is not None:
                msg = cmd.prepare(input_value)
            else:
                msg = cmd.prepare()
            if msg["ok"]:
                thread = cmd(msg["cmd"], msg, parent)
                self.threads.append(thread)
        self.threads[0].start()

    def partial_result(self, result):
        if result["returncode"] == 0:
            self.combined_result.update(result)
            self.threads.pop(0)

            if len(self.threads) > 0:
                self.threads[0].start()
            else:
                pyotherside.send('result', self.combined_result)
