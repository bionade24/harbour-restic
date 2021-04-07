import os
import tempfile
import pyotherside
from .restic_thread import ResticThread


class ResticCreateThread(ResticThread):
    def process_result(self, result):
        if result["returncode"] in [0, 1]:
            pass

    def log_event(self, msg):
        pyotherside.send("backup_log_event", msg)

    def started_event(self):
        pyotherside.send("backup_started_event", result)
        pyotherside.send("backup_log_event", "Backup started.")

    def finished_event(self, result):
        pyotherside.send("backup_finished_event", result)
        pyotherside.send("backup_log_event", "Backup finished.")

    @classmethod
    def prepare(cls, profile):
        """
        `restic init` is called from different places and needs some preparation.
        Centralize it here and return the required arguments to the caller.
        """
        ret = super().prepare(profile)
        if not ret["ok"]:
            return ret
        else:
            ret["ok"] = False  # Set back to false, so we can do our own checks here.

        n_backup_folders = len(ret["backup_include_paths"])
        if n_backup_folders == 0:
            ret["message"] = "Add some folders to back up first."
            return ret

        if not profile.repo.is_remote_repo() and not os.path.exists(profile.repo.url):
            ret["message"] = "Repo folder not mounted or moved."
            return ret

        cmd = ["restic", "backup", "-r", profile.repo.url, "--json"]

        # Add excludes
        # Partly inspired by resticmatic/resticmatic/restic/create.py
        if profile["exclude_rules"] is not None:
            exclude_dirs = []
            for p in profile["exclude_rules"].split("\n"):
                if p.strip():
                    expanded_directory = os.path.expanduser(p.strip())
                    exclude_dirs.append(expanded_directory)

            if exclude_dirs:
                pattern_file = tempfile.NamedTemporaryFile("w", delete=False)
                pattern_file.write("\n".join(exclude_dirs))
                pattern_file.flush()
                cmd.extend(["--exclude-from", pattern_file.name])

        if profile.exclude_if_present is not None:
            for f in profile.exclude_if_present.split("\n"):
                if f.strip():
                    cmd.extend(["--exclude-if-present", f.strip()])

        for f in profile["backup_include_paths"]:
            cmd.append(f.path)

        ret["message"] = "Starting backup.."
        ret["ok"] = True
        ret["cmd"] = cmd

        return ret
