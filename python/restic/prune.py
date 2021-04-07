import pyotherside
from .restic_thread import ResticThread


class ResticPruneThread(ResticThread):
    def log_event(self, msg):
        pyotherside.send("backup_log_event", msg)

    def started_event(self):
        pyotherside.send("backup_started_event")
        pyotherside.send("backup_log_event", "Pruning old snapshots..")

    def finished_event(self, result):
        pyotherside.send("backup_finished_event", result)
        pyotherside.send("result", result)

        if result["returncode"] == 0:
            pyotherside.send("backup_log_event", "Pruning done. No error reported.")
        else:
            pyotherside.send("backup_log_event", "Pruning done. There was an error.")

    @classmethod
    def prepare(cls, profile):
        ret = super().prepare(profile)
        if not ret["ok"]:
            return ret
        else:
            ret["ok"] = False  # Set back to false, so we can do our own checks here.

        cmd = ["restic", "-r", f"{profile.repo.url}", "prune", "--json"]

        ret["ok"] = True
        ret["cmd"] = cmd

        return ret
