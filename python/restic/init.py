import pyotherside
from .restic_thread import ResticThread
from .info import FakeProfile, FakeRepo


class ResticInitThread(ResticThread):
    def started_event(self):
        pyotherside.send("updated", "Setting up new repo...")

    @classmethod
    def prepare(cls, params):

        # Build fake profile because we don't have it in the DB yet.
        profile = FakeProfile(
            FakeRepo(params["backup_destination"], 999), "Init Repo", params["ssh_key"]
        )

        ret = super().prepare(profile)
        if not ret["ok"]:
            return ret
        else:
            ret["ok"] = False  # Set back to false, so we can do our own checks here.

        cmd = ["restic", "init", "-r", params["backup_destination"], "--json"]

        ret["password"] = params["password"]
        ret["ok"] = True
        ret["cmd"] = cmd

        return ret

    def process_result(self, result):
        if result["returncode"] == 0:
            pass  # TODO: Set repo_initialized== true
