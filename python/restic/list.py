import pyotherside
from dateutil import parser
from .restic_thread import ResticThread


class ResticListThread(ResticThread):
    def log_event(self, msg):
        pyotherside.send("backup_log_event", msg)

    def started_event(self):
        pyotherside.send("backup_started_event")
        pyotherside.send("backup_log_event", "Refreshing snapshots..")

    def finished_event(self, result):
        pyotherside.send("backup_finished_event", result)
        pyotherside.send("result", result)
        pyotherside.send("backup_log_event", "Refreshing snapshots done.")

    @classmethod
    def prepare(cls, profile):
        ret = super().prepare(profile)

        cls.profile = profile

        if not ret["ok"]:
            return ret
        else:
            ret["ok"] = False  # Set back to false, so we can do our own checks here.

        cmd = ["restic", "-r", profile.repo.url, "--json", "snapshots"]

        ret["ok"] = True
        ret["cmd"] = cmd

        return ret

    def process_result(self, result):
        if result["returncode"] == 0:
            pass  # TODO:
