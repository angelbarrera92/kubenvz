import os.path
import os
from dotenv import load_dotenv
import sys
import platform
import requests
from zipfile import ZipFile
from config import DOWNLOAD_PATH, VERSION_FILE
from .list import list_remote

""" Download Required kubectl / kustomize Versions """

def download_program(args, program, version):

    operating_sys = sys.platform
    # Upsert download path
    not os.path.exists(DOWNLOAD_PATH) and os.mkdir(DOWNLOAD_PATH)

    available_versions = list_remote(args)
    if version not in available_versions:
        print("Version '" + version + "' is not right available " + program + " version.\
            \nYou can check right available versions by running 'kubenvz kubectl/kustomize list remote'.\
            \nFor more informaion, Please refer kubenvz document https://github.com/aaratn/kubenvz#kubenvz-kubectlkustomize-list-remote.\n")
        sys.exit(1)

    if program == "kubectl":
        url = "https://github.com/kubernetes/kubectl/releases/download/v" + \
              version + "/kustomize_" + operating_sys + "_amd64"

    elif program == "kustomize":
        url = "https://github.com/kubernetes-sigs/kustomize/releases/download/v" + \
            version + "/kustomize_"+ version +"_" + operating_sys + "_amd64"

    if not os.path.exists(DOWNLOAD_PATH + program + "_" + version):

        print("Downloading", program, version, "from", url)

        binary = requests.get(url)

        if binary.status_code == 404:
            raise Exception("Invalid version, got 404 error !")

        dest_path = DOWNLOAD_PATH + program + "_" + version

        open(dest_path, 'wb').write(binary.content)

        if program == "kubectl":

            with ZipFile(dest_path, 'r') as zip:
                zip.extract('kubectl', path=DOWNLOAD_PATH)

            if os.path.exists(DOWNLOAD_PATH + '/' + program) and os.path.exists(dest_path):
                os.remove(dest_path)
                os.rename(DOWNLOAD_PATH + '/' + program, dest_path)

            else:
                raise Exception("Issue extracting kubectl !!")

        os.chmod(dest_path, 0o755)
    else:
        print (program, version, "already downloaded")

""" Installs Required kubectl / kustomize Versions """

def install(args):

    program = args.program
    version = args.version

    if not version and os.path.exists(VERSION_FILE):
        load_dotenv(dotenv_path=VERSION_FILE)
        version = (os.getenv(program.upper()))

    if not version:
        print("Please define version or add that to .kubenvz file.\
            \nYou don't need to mention version if you have .kubenvz file at current path. \
            \nFor more informaion, Please refer kubenvz document https://github.com/aaratn/kubenvz#kubenvz-file.\n")
        sys.exit(1)

    dest_path = DOWNLOAD_PATH + program + "_" + version

    if program == "kubectl":
        download_program(args, program, version)

    elif program == "kustomize":
        download_program(args, program, version)

    else:
        raise Exception(
            'Invalid Arguement !! It should be either kubectl / kustomize')

    if not os.access('/usr/local/bin', os.W_OK):
        print("Error: User doesn't have write permission of /usr/local/bin directory.\
            \n\nRun below command to grant permission and rerun 'kubenvz install' command.\
            \nsudo chown -R $(whoami) /usr/local/bin\n")
        sys.exit(1)

    try:
        os.remove("/usr/local/bin/" + program )

    except FileNotFoundError:
        pass

    os.symlink(dest_path, "/usr/local/bin/" + program )