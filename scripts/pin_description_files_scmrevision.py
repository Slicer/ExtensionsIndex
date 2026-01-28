"""
Python 3.x CLI for pinning extension description files.
"""

import glob
import json
import os
import sys
from urllib.parse import urlparse
from urllib.request import urlopen, HTTPError, Request


def parse_s4ext(ext_file_path):
    """Parse a Slicer extension description file.

    :param ext_file_path: Path to a Slicer extension description file.
    :return: Dictionary of extension metadata.
    """
    ext_metadata = {}
    try:
        with open(ext_file_path) as ext_file:
            for number, line in enumerate(ext_file):
                if not line.strip() or line.startswith("#"):
                    continue
                fields = [field.strip() for field in line.split(" ", 1)]
                if len(fields) > 2:
                    msg = f"Invalid line {number}: {line}"
                    raise ValueError(msg)
                ext_metadata[fields[0]] = fields[1] if len(fields) == 2 else None

    except FileNotFoundError:
        print(f"Failed to parse {ext_file_path}: File not found")
        return None

    except Exception as exc:
        print(f"An error occurred while parsing {ext_file_path}: {exc}")
        return None

    return ext_metadata


def update_s4ext(ext_file_path, metadata=None):
    """Update Slicer extension description file metadata.

    :param ext_file_path: Path to a Slicer extension description file.
    :param metadata: Dictionnary of metadata to use for updating the file.
    :return: True if the file was updated without error.
    """
    try:
        if metadata is None:
            metadata = {}

        # Read description file
        with open(ext_file_path) as ext_file:
            lines = list(ext_file)

        # Update content using provided metadata
        updated_lines = []
        for line in lines:
            empty_line = not line.strip()
            if empty_line or line.startswith("#"):
                updated_lines.append(line.strip())
                continue

            fields = [field for field in line.split(" ", 1)]
            key = fields[0]
            value = fields[1] if len(fields) > 1 else ""
            updated_value = metadata.get(key, value)
            updated_lines.append(f"{key} {updated_value}".strip())

        # Write updated description file
        with open(ext_file_path, "w") as ext_file:
            for line in updated_lines:
                ext_file.write(f"{line}\n")

        return True

    except FileNotFoundError:
        print(f"Failed to update {ext_file_path}: File not found")
        return False

    except Exception as exc:
        print(f"An error occurred while updating {ext_file_path}: {exc}")
        return False


def _gh_request(path, headers=None):
    try:
        # GitHub throttles down requests without a personal access token
        # Request yours under GitHub "Settings / Developer settings / Personal access tokens"
        token = os.environ.get("GITHUB_TOKEN", None)

        if headers is None:
            headers = {}
        if "Authorization" not in headers and token is not None:
            headers["Authorization"] = f"token {token}"

        url = f"https://api.github.com/{path}"
        request = Request(url, headers=headers)
        response = urlopen(request)
        return json.loads(response.read())

    except HTTPError as exc:
        error_msg = exc.read().decode("utf-8")
        print(f"Failed to retrieve information from GitHub using {url}")
        print(f"GitHub API Response: {error_msg}")
        return None

    except Exception as exc:
        print(f"An error occurred: {exc}")
        return None


def parse_scmurl(scmurl):
    """Parse Source Control URL and return host, owner and repo.

    :param url: Source Control URL.
    :return: tuple ``(host, owner, repo)`` or None if the URL can not be parsed.
    """
    try:
        if "@" in scmurl:
            # Convert from "git@host:owner/repo.git" to "https://host/owner/repo.git"
            scmurl = scmurl.replace(":", "/", 1).replace("git@", "https://", 1)

        # https URL
        result = urlparse(scmurl)
        if not result.netloc or not result.path:
            msg = "Invalid SCM URL format"
            raise ValueError(msg)

        # "/owner/repo.git" -> "owner/repo.git"
        path = result.path[1:]

        # "owner/repo.git" -> "owner/repo"
        path = path.replace(".git", "")

        owner, repo = path.split("/")[:2]
        return (result.netloc, owner, repo)

    except Exception as exc:
        print(f"An error occurred while parsing {scmurl}: {exc}")
        return None


class ExtensionProcessingError(RuntimeError):
    """Exception raised when a particular extension description file failed to be
    parsed, pinned or updated.
    """
    pass


def pin_s4ext(ext_file_path):
    """Update ``ext_file_path`` pinning scmrevision to the latest commit associated with
    the corresponding branch.

    :param ext_file_path: Path to a Slicer extension description file.
    :return: True if the file was pinned.
    :raises ExtensionProcessingError: if there was an error processing the decription file.
    """
    metadata = parse_s4ext(ext_file_path)
    if metadata is None:
        raise ExtensionProcessingError(ext_file_path)

    scmurl = metadata["scmurl"]
    scmrevision = metadata["scmrevision"]

    print("Parsed metadata:")
    print(f" - scmurl      : {scmurl}")
    print(f" - scmrevision : {scmrevision}")

    result = parse_scmurl(scmurl)
    if result is None:
        raise ExtensionProcessingError(ext_file_path)

    host, owner, repo = result
    print(f" - host        : {host}")
    print(f" - owner       : {owner}")
    print(f" - repo        : {repo}")

    if "github.com" not in host:
        return

    updated_metadata = {}

    pinned = False

    if scmrevision == "master":
        branch = scmrevision

        # Use GitHub API to get the latest commit
        commit_info = _gh_request(f"repos/{owner}/{repo}/commits/{branch}")
        if commit_info is None:
            raise ExtensionProcessingError(ext_file_path)
        git_sha = commit_info["sha"]
        updated_metadata["scmrevision"] = git_sha

        print("Pinning scmrevision to latest commit:")
        print(f" - branch       : {branch}")
        print(f" - latest commit: {git_sha}")

        pinned = True

    if not update_s4ext(ext_file_path, updated_metadata):
        raise ExtensionProcessingError(ext_file_path)

    return pinned


def main():
    # loop over all s4ext in the input directory
    if len(sys.argv) == 1:
        print(
            "Running this script will replace all occurrences of 'master' for scmrevision\n\
          with the master hash at the time script is run for the repositories hosted on GitHub.\n\
          To do this for all of the s4ext files in the current directory, pass 'all' as the argument.\n\
          To replace in specific s4ext files, pass the list of files separated by spaces."
        )
        sys.exit(1)
    elif sys.argv[1] == "all":
        s4extFileNames = glob.glob("*.s4ext")
    else:
        s4extFileNames = sys.argv[1:]

    pinned = []
    failed_pinned = []

    for s4extName in s4extFileNames:
        print("")
        print("Processing " + s4extName)
        try:
            if pin_s4ext(s4extName):
                pinned.append(s4extName)
        except ExtensionProcessingError as exc:
            failed_pinned.append(str(exc))

    print("")
    print(f"Pinned {len(pinned)} of {len(s4extFileNames)} description files.")

    if len(failed_pinned) > 0:
        print("")
        print(f"Failed to pin {len(failed_pinned)} description files")
        print("\n".join([f"- {failed}" for failed in failed_pinned]))
        sys.exit(len(failed_pinned))


if __name__ == "__main__":
    main()
