import os
import glob
import subprocess
import molbench.logger as log


def create_bash_files(files: list, command: str) -> list:
    bash_files = []
    basepath = os.getcwd()

    for f in files:
        fpath = os.path.dirname(f)
        os.chdir(fpath)
        infilename = os.path.basename(f)
        cmd = command.strip() + " " + infilename
        log.info(f"Now building script for {infilename} / {f}")
        subprocess.run(cmd, shell=True)
        log.debug(f"Executing command : {cmd}")

        fname_no_ext = os.path.splitext(infilename)[0]
        all_shs = glob.glob("*.sh")
        all_shs.extend(glob.glob("*.sbatch"))

        local_execs = [os.path.abspath(sh) for sh in all_shs
                       if fname_no_ext in sh]
        bash_files.extend(local_execs)
        os.chdir(basepath)
    return bash_files


def make_send_script(bashfiles: list, send_command: str,
                     sendscript_path: str):
    sendscript_content = """#!/bin/bash
function cd_and_sbatch() {
    local script_file=$1
    local folder=$2
    echo "Sending $script_file"
    cd "$folder" 
    """ + send_command.strip() + """ "$script_file"
    }\n\n"""

    for f in bashfiles:
        fpath = os.path.abspath(os.path.dirname(f))
        infilename = os.path.basename(f)

        addendum = f"cd_and_sbatch {infilename} {fpath}\n"
        sendscript_content += addendum

    with open(sendscript_path, "w") as f:
        f.write(sendscript_content)
