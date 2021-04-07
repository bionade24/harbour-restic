import subprocess
import re

SFSECRET_BIN = "/usr/bin/secrets-tool"


def create_collection(collection):
    command = [SFSECRET_BIN, "--create-collection", "--devicelock",
               "org.sailfishos.secrets.plugin.encryptedstorage.sqlcipher",
               collection]
    subprocess.run(command)


def collection_exists(collection):
    command = [SFSECRET_BIN, "--list-collections",
               "org.sailfishos.secrets.plugin.encryptedstorage.sqlcipher"]
    stdout = subprocess.run(command, stdout=subprocess.PIPE).stdout \
        .decode('UTF-8')
    return collection in stdout


def store_secret(collection, key, value):
    if not collection_exists(collection):
        create_collection(collection)
    command = [SFSECRET_BIN, "--store-collection-secret",
               "org.sailfishos.secrets.plugin.encryptedstorage.sqlcipher",
               collection, key, value]
    subprocess.run(command)


def secret_exists(collection, key):
    if not collection_exists(collection):
        return False
    # WARNING: Command not implemented upstream
    command = [SFSECRET_BIN, "--list-secrets",
               "org.sailfishos.secrets.plugin.encryptedstorage.sqlcipher",
               collection]
    stdout = subprocess.run(command, stdout=subprocess.PIPE).stdout \
        .decode('UTF-8')
    return key in stdout


def delete_secret(collection, key):
    command = [SFSECRET_BIN, "--delete-collection-secret",
               "org.sailfishos.secrets.plugin.encryptedstorage.sqlcipher",
               collection, key]
    subprocess.run(command)


def update_secret(collection, key, value):
    delete_secret(collection, key)
    store_secret(collection, key, value)


def get_secret(collection, key):
    command = [SFSECRET_BIN, "--get-collection-secret",
               "org.sailfishos.secrets.plugin.encryptedstorage.sqlcipher",
               collection, key]
    stdout = subprocess.run(command, stdout=subprocess.PIPE).stdout \
        .decode('UTF-8').replace("\n", "")
    return re.search(r'"(.*?)"', stdout).group(0).strip("\"")

