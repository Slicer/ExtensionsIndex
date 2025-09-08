#!/usr/bin/env python

"""
Python 3.x CLI for AI analysis of Slicer extensions.
"""

import argparse
import json
import os
import requests
import stat
import tempfile
import textwrap
import time
import subprocess
import shutil

# Use Nebula Block API endpoint for chat completions.
# It offers capable models for free with an OpenAI-compatible API.
INFERENCE_URL = "https://inference.nebulablock.com/v1/chat/completions"
INFERENCE_MODEL = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
INFERENCE_RESPONSE_PER_MINUTE_LIMIT = 3
INFERENCE_API_KEY = os.getenv("NEBULA_API_KEY")

QUESTIONS = [
    "Is there a EXTENSION_DESCRIPTION variable in the CMakeLists.txt file that describes what the extension does in a few sentences that can be understood by a person knowledgeable in medical image computing?",
    "Does the README.md file contain a short description, 1-2 sentences, which summarizes what the extension is usable for?",
    "Does the README.md file contain at least one image that illustrates what the extension can do, preferably a screenshot? Ignore contents of CMakeLists.txt file.",
    "Does the README.md file contain description of contained modules: at one sentence for each module?",
    "Does the README.md file contain publication: link to publication and/or to PubMed reference or a 'How to cite' section?",
    "Does the documentation contain step-by-step tutorial? Does the tutorial tell where to get sample data from?"
    "Does this code download any executable code from the internet or uploads any data to the internet?",
    "Is any code executed at the file scope when a module is imported?",
    "Are any Python packages imported at the file scope that are not from the Python Standard Library and not from Slicer, vtk, SimpleITK, numpy, and scipy?",
    "Does it directly use pip_install to install pytorch?",
    "Does it store large amount of downloaded content on local disk other than installing Python packages? Does it provide a way for the user to remove that content?",
]

def parse_json(extension_file_path):
    """Parse a Slicer extension description file.
    :param extension_file_path: Path to a Slicer extension description file (.json).
    :return: Dictionary of extension metadata.
    """
    with open(extension_file_path) as input_file:
        try:
            return json.load(input_file)
        except json.JSONDecodeError as exc:
            extension_name = os.path.splitext(os.path.basename(extension_file_path))[0]
            raise ExtensionParseError(
                extension_name,
                textwrap.dedent("""
                Failed to parse '%s': %s
                """ % (extension_file_path, exc)))


def safe_cleanup_directory(directory_path, max_attempts=3):
    """Safely remove a directory with retries and permission handling."""
    if not directory_path or not os.path.exists(directory_path):
        return

    def force_remove_readonly(func, path, exc_info):
        """Error handler for Windows readonly files"""
        try:
            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)
        except Exception:
            pass  # Ignore errors in the error handler

    for attempt in range(max_attempts):
        try:
            shutil.rmtree(directory_path, onexc=force_remove_readonly)
            return True  # Success
        except (OSError, PermissionError) as e:
            if attempt < max_attempts - 1:
                time.sleep(1)  # Wait longer before retrying
                continue
            else:
                print(f"Warning: Failed to clean up directory after {max_attempts} attempts: {directory_path}\n{e}")
        except Exception as e:
            print(f"Warning: Error cleaning up directory: {directory_path}\n{e}")


def clone_repository(metadata, cloned_repository_folder):
    """Clone a git repository to a temporary directory."""
    scm_url = metadata.get("scm_url")
    scm_revision = metadata.get("scm_revision")

    print(f"Repository URL: {scm_url}")
    if scm_revision:
        print(f"Repository revision: {scm_revision}")

    if scm_revision:
        subprocess.run(
            ['git', 'clone', scm_url, cloned_repository_folder],
            check=True, capture_output=True, text=True, timeout=300)
        subprocess.run(
            ['git', 'checkout', scm_revision],
            cwd=cloned_repository_folder,
            check=True, capture_output=True, text=True, timeout=300)
    else:
        subprocess.run(
            ['git', 'clone', '--depth', '1', scm_url, cloned_repository_folder],
            check=True, capture_output=True, text=True, timeout=600)


def collect_analyzed_files(folder):
    """Load all .py files in a folder, recursively."""
    scripts = {}
    for root, dirs, files in os.walk(folder):
        for filename in files:
            fullpath = os.path.join(root, filename)
            relative_path = os.path.relpath(fullpath, start=folder).replace("\\", "/")
            if filename.endswith(".py") or filename.endswith(".md") or relative_path == "CMakeLists.txt":
                with open(fullpath, "r", encoding="utf-8") as f:
                    # get relative path to folder, in linux-style
                    scripts[relative_path] = f.read()
    return scripts


def analyze_extension(extension_name, metadata, cloned_repository_folder):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {INFERENCE_API_KEY}"
    }

    scripts = collect_analyzed_files(cloned_repository_folder)

    system_msg = \
        "You are a quality control expert that checks community-contributed files that contain code and documentation." \
        " Do not talk about things in general, only strictly about the content provided." \
        " Relevant files of the extension repository are provided below." \
        " Each file is delimited by lines with '=== FILE: filename ===' and '=== END FILE: filename ==='."
    for filename in scripts:
        system_msg += f"\n=== FILE: {filename} ===\n"
        system_msg += scripts[filename]
        system_msg += f"\n=== END FILE: {filename} ===\n"

    # Send the system prompt only once, then continue the conversation
    messages = [
        {"role": "system", "content": system_msg}
    ]

    for index, question in enumerate(QUESTIONS):
        messages.append({"role": "user", "content": question})
        data = {
            "messages": messages,
            "model": INFERENCE_MODEL,
            "max_tokens": None,
            "temperature": 1,
            "top_p": 0.9,
            "stream": False
        }
        response = requests.post(INFERENCE_URL, headers=headers, json=data)
        print("\n------------------------------------------------------")
        print(f"Question {index+1}: {question}")
        print("------------------------------------------------------")
        try:
            answer = response.json()["choices"][0]["message"]["content"]

            print(answer)
            messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            print("Error or unexpected response:", response.json()["error"]["message"])
            if index == 0:
                # if the first question fails, likely the system prompt is too long, so stop here
                raise RuntimeError("Stopping further questions since the first question failed.")

        # wait according to response per minute limit
        delay = 60 / INFERENCE_RESPONSE_PER_MINUTE_LIMIT
        import time
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(
        description='AI analysis of extensions.')
    parser.add_argument("extension_description_files", nargs='*', help="Extension JSON files to validate")
    args = parser.parse_args()

    extension_descriptions_folder = "."

    print("AI analysis of 3D Slicer extensions\n")

    success = True

    for file_path in args.extension_description_files:

        # Get extension name and desctiption file path
        file_extension = os.path.splitext(file_path)[1]
        if file_extension != '.json':
            # not an extension description file, ignore it
            continue
        full_path = os.path.join(extension_descriptions_folder, file_path)
        if not os.path.isfile(full_path):
            # not a file in the extensions descriptions folder, ignore it
            continue
        extension_name = os.path.splitext(os.path.basename(file_path))[0]

        print(f"Extension: {extension_name}")
        print("=====================================================")

        metadata = parse_json(file_path)
        cloned_repository_folder = tempfile.mkdtemp(prefix=f"extension_check_{extension_name}_")

        try:
            clone_repository(metadata, cloned_repository_folder)
            analyze_extension(extension_name, metadata, cloned_repository_folder)
        finally:
            # Clean up temporary directory
            success_cleanup = safe_cleanup_directory(cloned_repository_folder)

        print("=====================================================")


if __name__ == "__main__":
    import sys
    main()
