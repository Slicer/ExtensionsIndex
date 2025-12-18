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


# Get inference server configuration from environment variables
INFERENCE_URL = os.getenv("INFERENCE_URL")
if not INFERENCE_URL:
    raise ValueError("INFERENCE_URL environment variable is not set. Please set it before running the script.")
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")
if not INFERENCE_MODEL:
    raise ValueError("INFERENCE_MODEL environment variable is not set. Please set it before running the script.")
INFERENCE_API_KEY = os.getenv("INFERENCE_API_KEY")
if not INFERENCE_API_KEY:
    raise ValueError("INFERENCE_API_KEY environment variable is not set. Please set it before running the script.")

INFERENCE_RESPONSE_PER_MINUTE_LIMIT = 10 #  slow down to not exceed token per minute (tpm) limit
INFERENCE_MAX_CHARACTERS = 400000  # max characters in all files provided to the model, approximately 100k tokens

print(f"Using inference server: {INFERENCE_URL} with model: {INFERENCE_MODEL}, with API key: {'*' * (len(INFERENCE_API_KEY)-3) + INFERENCE_API_KEY[-3:]}    ")

QUESTIONS = [
    ["Is there a EXTENSION_DESCRIPTION variable in the CMakeLists.txt file that describes what the extension does in a few sentences that can be understood by a person knowledgeable in medical image computing?", ["cmake"]],
    ["Does the README.md file contain a short description, 1-2 sentences, which summarizes what the extension is usable for?", ["doc"]],
    ["Does the README.md file contain at least one image that illustrates what the extension can do, preferably a screenshot?", ["doc"]],
    ["Does the README.md file contain description of contained modules: at one sentence for each module?", ["doc"]],
    ["Does the README.md file contain publication: link to publication and/or to PubMed reference or a 'How to cite' section?", ["doc"]],
    ["Does the documentation contain step-by-step tutorial? Does the tutorial tell where to get sample data from?", ["doc"]],
    ["Does this code download any executable code from the internet or uploads any data to the internet?", ["source"]],
    ["Is any code executed at the file scope when a module is imported?", ["source"]],
    ["Are any Python packages imported at the file scope that are not from the Python Standard Library and not from Slicer, vtk, SimpleITK, numpy, and scipy?", ["source"]],
    ["Does it directly use pip_install to install pytorch?", ["source"]],
    ["Does it store large amount of downloaded content on local disk other than installing Python packages? Does it provide a way for the user to remove that content?", ["source"]],
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
    """Load all .py files in a folder, recursively.
    returns a dict of categories (doc, source, cmake), each containing a dict of filename->content"""
    found_files = { "doc": {}, "source": {}, "cmake": {} }
    for root, dirs, files in os.walk(folder):
        for filename in files:
            fullpath = os.path.join(root, filename)
            relative_path = os.path.relpath(fullpath, start=folder).replace("\\", "/")
            category = None
            if filename.endswith(".py"):
                category = "source"
            elif filename.endswith(".md"):
                category = "doc"
            elif relative_path == "CMakeLists.txt":
                category = "cmake"
            if category is None:
                continue
            with open(fullpath, "r", encoding="utf-8") as f:
                # get relative path to folder, in linux-style
                found_files[category][relative_path] = f.read()
    return found_files

def ask_question(system_msg, question):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {INFERENCE_API_KEY}",
        "HTTP-Referer": "slicer.org", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "3D Slicer", # Optional. Site title for rankings on openrouter.ai.
    }

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": question}
    ]

    data = {
        "messages": messages,
        "model": INFERENCE_MODEL,
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }

    response = requests.post(INFERENCE_URL, headers=headers, json=data)

    # wait according to response per minute limit
    delay = 60 / INFERENCE_RESPONSE_PER_MINUTE_LIMIT
    import time
    time.sleep(delay)

    try:
        answer = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Request data: {data}", file=sys.stderr)
        print(f"Response status code: {response.status_code}", file=sys.stderr)
        print(f"Response content: {response.text}", file=sys.stderr)
        raise RuntimeError(f"Error or unexpected response: {response.json()["error"]["message"]}")

    return answer


def analyze_extension(extension_name, metadata, cloned_repository_folder):

    files = collect_analyzed_files(cloned_repository_folder)

    for index, [question, categories] in enumerate(QUESTIONS):

        print("\n------------------------------------------------------")
        print(f"Question {index+1}: {question}")
        print("------------------------------------------------------")

        file_content_batches = [""]

        # Add files of the categories relevant for the question
        # The context of each query is limited, therefore if there are too many/too large input files in the relevant categories,
        # then we split them into batches, ask the question for each batch, and then generate a summary of the answers.
        for category in categories:
            files_in_category = files.get(category, {})
            for filename in files_in_category:
                next_file = f"\n=== FILE: {filename} ===\n" + files_in_category[filename] + f"\n=== END FILE: {filename} ===\n"
                if (not file_content_batches[-1].strip()) or (len(file_content_batches[-1]) + len(next_file) < INFERENCE_MAX_CHARACTERS):
                    # We can add this file to the current batch
                    file_content_batches[-1] += next_file
                else:
                    # Start a new batch
                    file_content_batches.append(next_file)

        if not file_content_batches[0].strip():
            print("No relevant files found for this question.")
            continue

        role_description = \
            "You are a quality control expert that checks community-contributed files that contain code and documentation." \
            " Do not talk about things in general, only strictly about the content provided."

        answers = []

        for batch_index, file_content in enumerate(file_content_batches):

            system_msg = role_description
            system_msg += " Relevant files of the extension repository are provided below."
            system_msg += " Each file is delimited by lines with '=== FILE: filename ===' and '=== END FILE: filename ==='.\n"
            system_msg += file_content

            try:
                answer = ask_question(system_msg, question)
                answers.append(answer)
            except Exception as e:
                answers = [f"Error or unexpected response: {e}"]
                break

        if len(answers) == 1:
            print(answers[0])
        else:
            # Multiple batches of files were used to answer this question, generate a summary
            system_msg = role_description
            question = "The answer to the question is spread over multiple parts. Please summarize the answer in a concise way, combining all relevant information from the different parts. " \
                "Here are the different parts of the answer:\n\n"
            for part_index, part in enumerate(answers):
                question += f"--- PART {part_index+1} ---\n{part}\n"
            try:
                answer = ask_question(system_msg, question)
            except Exception as e:
                answer = f"Error or unexpected response: {e}"
            print(answer)


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

        print("\n=====================================================\n")


if __name__ == "__main__":
    import sys
    main()
