import pyotherside
from .restic_thread import ResticThread


class ResticMountThread(ResticThread):
    def started_event(self):
        pyotherside.send('updated', "Mounting archive into folder...")

    @classmethod
    def prepare(cls, profile):
        ret = super().prepare(profile)
        if not ret["ok"]:
            return ret
        else:
            ret["ok"] = False  # Set back to false, so we can do our own checks here.

        cmd = ["restic", "--json", "-r", f"{profile.repo.url}", "mount", "mountpoint"]

        ret["ok"] = True
        ret["cmd"] = cmd

        return ret
