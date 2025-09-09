#!/usr/bin/env python

"""
Python 3.x CLI for validating extension description files with enhanced reporting.
"""

import argparse
import json
import os
import stat
import tempfile
import textwrap
import time
import urllib.parse as urlparse
import subprocess
import re
import shutil
from datetime import datetime
from functools import wraps
from pathlib import Path

# Import optional dependencies for JSON schema validation
jsonschema = None
requests = None
try:
    import jsonschema
    import requests
except ImportError as e:
    print(f"Warning: JSON schema validation dependencies not available: {e}")
    print("Install with: pip install jsonschema requests")

class ExtensionDependencyError(RuntimeError):
    """Exception raised when a particular extension description file failed to be parsed.
    """
    def __init__(self, error_list):
        self.error_list = error_list

    def __str__(self):
        return "\n".join(self.error_list)

class ExtensionParseError(RuntimeError):
    """Exception raised when a particular extension description file failed to be parsed.
    """
    def __init__(self, extension_name, details):
        self.extension_name = extension_name
        self.details = details

    def __str__(self):
        return self.details


class ExtensionCheckError(RuntimeError):
    """Exception raised when a particular extension check failed.
    """
    def __init__(self, extension_name, check_name, details):
        self.extension_name = extension_name
        self.check_name = check_name
        self.details = details

    def __str__(self):
        return self.details


def require_metadata_key(metadata_key, value_required=True):
    check_name = "require_metadata_key"

    def dec(fun):
        @wraps(fun)
        def wrapped(*args, **kwargs):
            extension_name = args[0]
            metadata = args[1]
            if metadata_key not in metadata.keys():
                raise ExtensionCheckError(extension_name, check_name, "%s key is missing" % metadata_key)
            if value_required and metadata[metadata_key] is None:
                raise ExtensionCheckError(extension_name, check_name, "%s value is not set" % metadata_key)
            return fun(*args, **kwargs)
        return wrapped
    return dec


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

def check_json_file_format(extension_name, metadata, extension_file_path):
    """Check if the JSON file is properly formatted."""
    check_name = "check_json_file_format"
    try:
        with open(extension_file_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Invalid JSON format: {str(e)}")
    # Force using LF-only line endings
    with open(extension_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '\r\n' in content or '\r' in content:
        raise ExtensionCheckError(
            extension_name, check_name,
            "File contains non-LF line endings (CR or CRLF). Please convert to LF-only line endings.")

def check_json_schema(extension_name, metadata):
    """Validate extension description JSON against its referenced schema."""
    check_name = "check_json_schema"

    if not jsonschema or not requests:
        raise ExtensionCheckError(
            extension_name, check_name,
            "JSON schema validation requires 'jsonschema' and 'requests' packages. Install with: pip install jsonschema requests")

    # Check if $schema is present
    if "$schema" not in metadata:
        raise ExtensionCheckError(
            extension_name, check_name,
            "No $schema field found in extension description")

    schema_url = metadata["$schema"]
    if not schema_url:
        raise ExtensionCheckError(
            extension_name, check_name,
            "$schema field is empty")

    # Remove fragment identifier if present (e.g., #/ at the end)
    if "#" in schema_url:
        schema_url = schema_url.split("#")[0]

    try:
        # Download the schema
        response = requests.get(schema_url, timeout=30)
        response.raise_for_status()
        schema = response.json()
    except requests.RequestException as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Failed to download schema from {schema_url}: {str(e)}")
    except json.JSONDecodeError as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Invalid JSON schema at {schema_url}: {str(e)}")

    try:
        # Validate the extension metadata against the schema
        jsonschema.validate(metadata, schema)
    except jsonschema.ValidationError as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"JSON schema validation failed: {e.message} at path: {' -> '.join(str(p) for p in e.absolute_path)}")
    except jsonschema.SchemaError as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Invalid schema: {str(e)}")


@require_metadata_key("category")
def check_category(extension_name, metadata):
    category = metadata["category"]
    if category not in ACCEPTED_EXTENSION_CATEGORIES:
        raise ExtensionCheckError(extension_name, "check_category", f"Category **`{category}`** is unknown. Consider using any of the known extensions instead: `{'`, `'.join(ACCEPTED_EXTENSION_CATEGORIES)}`")


@require_metadata_key("scm_url")
def check_scm_url_syntax(extension_name, metadata):
    check_name = "check_scm_url_syntax"

    if "://" not in metadata["scm_url"]:
        raise ExtensionCheckError(extension_name, check_name, "scm_url do not match scheme://host/path")

    supported_schemes = ["git", "https"]
    scheme = urlparse.urlsplit(metadata["scm_url"]).scheme
    if scheme not in supported_schemes:
        raise ExtensionCheckError(
            extension_name, check_name,
            "scm_url scheme is '%s' but it should by any of %s" % (scheme, supported_schemes))

def check_extension_name(extension_name, metadata):
    check_name = "check_extension_name"

    if extension_name in EXTENSION_NAME_CHECK_EXCEPTIONS:
        return

    if extension_name.lower().startswith("slicer"):

        raise ExtensionCheckError(
            extension_name, check_name,
            textwrap.dedent("""
            extension name should not start with 'Slicer'. Please, consider changing it to '%s'.
            """ % (
                extension_name[6:],)))

@require_metadata_key("scm_url")
def check_git_repository_name(extension_name, metadata):
    """See https://www.slicer.org/wiki/Documentation/Nightly/Developers/FAQ#Should_the_name_of_the_source_repository_match_the_name_of_the_extension_.3F
    """
    check_name = "check_git_repository_name"

    repo_name = os.path.splitext(urlparse.urlsplit(metadata["scm_url"]).path.split("/")[-1])[0]

    if repo_name in REPOSITORY_NAME_CHECK_EXCEPTIONS:
        return

    if "slicer" not in repo_name.lower():

        variations = [prefix + repo_name for prefix in ["Slicer-", "Slicer_", "SlicerExtension-", "SlicerExtension_"]]

        raise ExtensionCheckError(
            extension_name, check_name,
            textwrap.dedent("""
            extension repository name is '%s'. Please, consider changing it to 'Slicer%s' or any of
            these variations %s.
            """ % (
                repo_name, repo_name, variations)))

@require_metadata_key("scm_url")
def check_git_repository_topics(extension_name, metadata):
    """See https://www.slicer.org/wiki/Documentation/Nightly/Developers/FAQ#Should_the_name_of_the_source_repository_match_the_name_of_the_extension_.3F
    """
    check_name = "check_git_repository_topics"

    # Example: scm_url = "https://github.com/ciroraggio/SlicerModalityConverter.git"

    scm_url = metadata["scm_url"]
    parsed_url = urlparse.urlsplit(scm_url)
    if parsed_url.netloc.lower() != "github.com":
        # Only GitHub repositories are required to use the slicer-extension topic
        print("Skipping repository topics check for non-GitHub repository:", scm_url)
        return

    owner = parsed_url.path.split("/")[1]
    repo = os.path.splitext(parsed_url.path.split("/")[-1])[0]

    import requests
    url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    topics = []
    if response.status_code == 200:
        data = response.json()
        topics = data.get("names", [])
    else:
        raise ValueError(f"Failed to get github topics for {owner}/{repo}: Error {response.status_code}: {response.text}")

    if "3d-slicer-extension" not in topics:
        raise ExtensionCheckError(
            extension_name, check_name,
            textwrap.dedent("""
            GitHub repository does not have the '3d-slicer-extension' topic. Please, add it to the repository topics.
            """))

def validate_image_url(url, url_type, extension_name, check_name):
    """Validate that a URL points to a valid image file."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '').lower()

        # Check if it's a valid image content type or if the URL suggests it's an image
        valid_image_types = ['image/png', 'image/jpeg', 'image/gif']
        is_valid_content_type = any(img_type in content_type for img_type in valid_image_types)

        # Allow application/octet-stream only if the URL ends with an image extension
        if not is_valid_content_type:
            if 'application/octet-stream' in content_type:
                # Check if URL has image file extension
                if not any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                    raise ExtensionCheckError(
                        extension_name, check_name,
                        f"{url_type} '{url}' returns 'application/octet-stream' but URL doesn't have an image file extension")
            else:
                raise ExtensionCheckError(
                    extension_name, check_name,
                    f"{url_type} '{url}' does not point to a valid image (Content-Type: {content_type})")
    except requests.RequestException as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Failed to download {url_type.lower()} from {url_type} '{url}': {str(e)}")

def safe_cleanup_directory(directory_path, max_attempts=3):
    """Safely remove a directory with retries and permission handling."""
    if not directory_path or not os.path.exists(directory_path):
        return True

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
                print(f"Warning: Failed to clean up directory after {max_attempts} attempts: {directory_path}")
                print(f"Error: {e}")
                return False
        except Exception as e:
            print(f"Warning: Unexpected error cleaning up directory: {directory_path}")
            print(f"Error: {e}")
            return False


def check_clone_repository(extension_name, metadata, cloned_repository_folder):
    """Clone a git repository to a temporary directory."""
    scm_url = metadata.get("scm_url")
    scm_revision = metadata.get("scm_revision")

    print(f"Repository URL: {scm_url}\n")
    if scm_revision:
        print(f"Repository revision: {scm_revision}\n")

    try:
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
    except subprocess.TimeoutExpired as e:
        raise ExtensionCheckError(extension_name, "clone_repository", f"Git clone operation timed out: {e}")
    except subprocess.CalledProcessError as e:
        raise ExtensionCheckError(extension_name, "clone_repository", f"Failed to clone repository: {e.stderr.strip() if e.stderr else 'Unknown git error'}")
    except FileNotFoundError:
        raise ExtensionCheckError(extension_name, "clone_repository", "Git command not found. Please ensure git is installed and in PATH")


def check_cmakelists_content(extension_name, metadata, cloned_repository_folder=None):
    """Check if the top-level CMakeLists.txt file project name matches the extension name."""
    check_name = "check_cmakelists_content"

    # Look for CMakeLists.txt in the cloned repository
    if not cloned_repository_folder:
        raise ExtensionCheckError(
            extension_name, check_name,
            "Repository is not available.")
    cmake_file_path = os.path.join(cloned_repository_folder, "CMakeLists.txt")
    if not os.path.isfile(cmake_file_path):
        raise ExtensionCheckError(
            extension_name, check_name,
            "CMakeLists.txt file not found in repository root")

    # Read and parse CMakeLists.txt
    try:
        with open(cmake_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            cmake_content = f.read()
    except Exception as e:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Failed to read CMakeLists.txt: {str(e)}")

    extension_name_in_cmake = None

    # Parse CMakeLists.txt to find project() declaration
    # Look for patterns like: project(ExtensionName) or project(ExtensionName VERSION ...)
    # Handle multi-line project declarations and various whitespace
    project_pattern = r'project\s*\(\s*([^\s\)\n\r]+)'
    matches = re.findall(project_pattern, cmake_content, re.IGNORECASE | re.MULTILINE)
    if matches:
        extension_name_in_cmake = matches[0].strip().strip('"').strip("'")

    # if PROJECT name is not specified then fall back to the old EXTENSION_NAME variable
    if not extension_name_in_cmake:
        extension_name_pattern = r'set\(EXTENSION_NAME\s+([^\s\)]+)\)'
        extension_name_matches = re.findall(extension_name_pattern, cmake_content, re.IGNORECASE | re.MULTILINE)
        if extension_name_matches:
            extension_name_in_cmake = extension_name_matches[0].strip().strip('"').strip("'")

    if not extension_name_in_cmake:
        raise ExtensionCheckError(
            extension_name, check_name,
            "No project() declaration found in CMakeLists.txt")

    # Check if the project name matches the extension name
    if extension_name_in_cmake != extension_name:
        raise ExtensionCheckError(
            extension_name, check_name,
            f"Extension name in CMakeLists.txt project name '{extension_name_in_cmake}' does not match extension description file name '{extension_name}'")

    # Check extension icon URL
    # set(EXTENSION_ICONURL "https://raw.githubusercontent.com/jamesobutler/ModelClip/main/Resources/Icons/ModelClip.png")
    extension_icon_url = None
    icon_url_pattern = r'set\s*\(EXTENSION_ICONURL\s*"([^"]+)"[ ]*\)'
    icon_url_matches = re.findall(icon_url_pattern, cmake_content, re.IGNORECASE | re.MULTILINE)
    if icon_url_matches:
        extension_icon_url = icon_url_matches[0].strip()
        if not extension_icon_url.startswith("http"):
            raise ExtensionCheckError(
                extension_name, check_name,
                f"EXTENSION_ICONURL '{extension_icon_url}' should be a valid URL starting with 'http'")
    if not extension_icon_url:
        raise ExtensionCheckError(
            extension_name, check_name,
            "No EXTENSION_ICONURL found in CMakeLists.txt.")

    # Validate the icon URL
    validate_image_url(extension_icon_url, "EXTENSION_ICONURL", extension_name, check_name)
    print(f"- :white_check_mark: Extension icon URL: {extension_icon_url}\n")

    # Check screenshot URLS
    # set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/SlicerProstate/SlicerZFrameRegistration/master/Screenshots/1.png https://raw.githubusercontent.com/SlicerProstate/SlicerZFrameRegistration/master/Screenshots/2.png")
    extension_screenshot_urls = []
    screenshot_urls_pattern = r'set\s*\(EXTENSION_SCREENSHOTURLS\s*"([^"]+)"\)'
    screenshot_urls_matches = re.findall(screenshot_urls_pattern, cmake_content, re.IGNORECASE | re.MULTILINE)
    if screenshot_urls_matches:
        extension_screenshot_urls = [url.strip() for url in screenshot_urls_matches[0].split()]
        for url in extension_screenshot_urls:
            if not url.startswith("http"):
                raise ExtensionCheckError(
                    extension_name, check_name,
                    f"EXTENSION_SCREENSHOTURLS '{url}' should be a valid URL starting with 'http'")
    if not extension_screenshot_urls:
        raise ExtensionCheckError(
            extension_name, check_name,
            "No EXTENSION_SCREENSHOTURLS found in CMakeLists.txt.")

    for url in extension_screenshot_urls:
        validate_image_url(url, "EXTENSION_SCREENSHOTURLS", extension_name, check_name)
        print(f"- :white_check_mark: Extension screenshot URL: {url}")

    # Log the top-level CMakeLists.txt file content
    return f"\nTop-level CMakeLists.txt content:\n```\n{cmake_content}\n```\n"


def check_license_file(extension_name, metadata, cloned_repository_folder):
    # Find license file
    license_file_path = None
    license_file_names = ["LICENSE", "LICENCE", "License.txt", "license.txt", "LICENSE.txt", "COPYING", "COPYING.txt"]
    for license_file_name in license_file_names:
        potential_path = os.path.join(cloned_repository_folder, license_file_name)
        if os.path.isfile(potential_path):
            license_file_path = potential_path
            break
    if not license_file_path:
        if extension_name in LICENSE_CHECK_EXCEPTIONS:
            print(f"- :warning: No license file found in {extension_name} repository root. This is a known issue - skipping check.")
            return
        raise ExtensionCheckError(
            extension_name, "check_license_file",
            "No license file found in repository root.")
    # Print the LICENSE.txt file content
    with open(license_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        license_content = f.read()
    if len(license_content) > 1000:
        license_content = license_content[:1000] + "...\n"
    return f"\nLicense file ({os.path.basename(license_file_path)}) content:\n```\n{license_content}\n```\n"


def check_dependencies(directory):
    import os
    required_extensions = {}  # for each extension it contains a list of extensions that require it
    available_extensions = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if not os.path.isfile(f) or not filename.endswith(".json"):
            continue
        extension_name, extension = os.path.splitext(os.path.basename(filename))
        if extension != ".json":
            continue
        try:
            extension_description = parse_json(f)
        except ExtensionParseError as exc:
            print(exc)
            continue
        available_extensions.append(extension_name)
        if 'build_dependencies' not in extension_description:
            continue
        dependencies = extension_description['build_dependencies']
        for dependency in dependencies:
            if not dependency:
                continue
            if dependency in required_extensions:
                required_extensions[dependency].append(extension_name)
            else:
                required_extensions[dependency] = [extension_name]

    print(f"Checked dependency between {len(available_extensions)} extensions.\n")
    errors_found = []
    for extension in required_extensions:
        if extension in available_extensions:
            # required extension is found
            continue
        required_by_extensions = ', '.join(required_extensions[extension])
        errors_found.append(f"'{extension}' extension is not found. It is required by extension: {required_by_extensions}.")
    if errors_found:
        raise ExtensionDependencyError(errors_found)


def print_categories(directory):
    import os
    extensions_for_categories = {}  # for each category it contains a list of extensions
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if not os.path.isfile(f) or not filename.endswith(".json"):
            continue
        extension_name, extension = os.path.splitext(os.path.basename(filename))
        if extension != ".json":
            continue
        try:
            extension_description = parse_json(f)
        except ExtensionParseError as exc:
            print(exc)
            continue
        category = extension_description.get("category", "")
        if not category:
            continue
        if extensions_for_categories.get(category) is None:
            extensions_for_categories[category] = []
        extensions_for_categories[category].append(extension_name)
    print(f"[\n{'\n'.join(f'    "{category}",' for category in sorted(extensions_for_categories.keys()))}\n]")


def main():
    parser = argparse.ArgumentParser(
        description='Validate extension description files.')
    parser.add_argument("extension_description_files", nargs='*', help="Extension JSON files to validate")
    parser.add_argument("--print-categories", action='store_true',
                        help="Print categories of extensions in the specified folder and quit.")
    args = parser.parse_args()

    extension_descriptions_folder = "."

    if args.print_categories:
        print_categories(extension_descriptions_folder)
        return 0

    print("# Check extension description files\n")

    success = True

    failed_extensions = set()
    found_extensions = []
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
        found_extensions.append(extension_name)

        print(f"## Extension: {extension_name}")

        # Log the description file content for convenience
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            description_file_content = f.read()
        print(f"Extension description file content:\n```\n{description_file_content}\n```\n")

        try:
            metadata = parse_json(file_path)
        except ExtensionParseError as exc:
            print(f"- :x: Failed to parse extension description file: {exc}")
            success = False
            failed_extensions.add(extension_name)
            continue

        cloned_repository_folder = tempfile.mkdtemp(prefix=f"extension_check_{extension_name}_")

        extension_description_checks = [
            ("Clone repository", check_clone_repository, {"cloned_repository_folder": cloned_repository_folder}),
            ("Check JSON schema", check_json_schema, {}),
            ("Check JSON file format", check_json_file_format, {"extension_file_path": file_path}),
            ("Check extension name", check_extension_name, {}),
            ("Check category", check_category, {}),
            ("Check git repository name", check_git_repository_name, {}),
            ("Check git repository topics", check_git_repository_topics, {}),
            ("Check SCM URL syntax", check_scm_url_syntax, {}),
            ("Check CMakeLists.txt content", check_cmakelists_content, {"cloned_repository_folder": cloned_repository_folder}),
            ("Check license file", check_license_file, {"cloned_repository_folder": cloned_repository_folder}),
            ]
        for check_description, check, check_kwargs in extension_description_checks:
            try:
                details = check(extension_name, metadata, **check_kwargs)
                print(f"- :white_check_mark: {check_description} completed successfully")
                if details:
                    print(details)
            except ExtensionCheckError as exc:
                print(f"- :x: {check_description} failed: {exc}")
                failed_extensions.add(extension_name)
                success = False

        # Clean up temporary directory
        if cloned_repository_folder:
            success_cleanup = safe_cleanup_directory(cloned_repository_folder)
            if not success_cleanup:
                print(f"Note: Temporary directory may still exist: {cloned_repository_folder}")

    if len(found_extensions) > 1:
        print("## Extensions test summary")
        print(f"Checked {len(found_extensions)} extension description files.")
        if failed_extensions:
            print(f"- :x: Checks failed for {len(failed_extensions)} extensions: {', '.join(failed_extensions)}")

    try:
        print("## Extension dependencies")
        check_dependencies(extension_descriptions_folder)
        print(":white_check_mark: Dependency check completed successfully")
    except ExtensionDependencyError as exc:
        print(f":x: Dependency check failed: {exc}")
        success = False

    return 0 if success else 1


REPOSITORY_NAME_CHECK_EXCEPTIONS = [
    "3DMetricTools",
    "ai-assisted-annotation-client",
    "aigt",
    "AnglePlanes-Extension",
    "AnomalousFiltersExtension",
    "BoneTextureExtension",
    "CarreraSlice",
    "ChangeTrackerPy",
    "CMFreg",
    "CurveMaker",
    "DatabaseInteractorExtension",
    "dcmqi",
    "DSC_Analysis",
    "EasyClip-Extension",
    "ErodeDilateLabel",
    "FilmDosimetryAnalysis",
    "GelDosimetryAnalysis",
    "GyroGuide",
    "iGyne",
    "ImageMaker",
    "IntensitySegmenter",
    "MeshStatisticsExtension",
    "MeshToLabelMap",
    "ModelClip",
    "MONAILabel",
    "mpReview",
    "NeedleFinder",
    "opendose3d",
    "OsteotomyPlanner",
    "PBNRR",
    "PedicleScrewSimulator",
    "PercutaneousApproachAnalysis",
    "PerkTutor",
    "PET-IndiC",
    "PETLiverUptakeMeasurement",
    "PETTumorSegmentation",
    "PickAndPaintExtension",
    "PkModeling",
    "PortPlacement",
    "Q3DCExtension",
    "QuantitativeReporting",
    "ResectionPlanner",
    "ScatteredTransform",
    "Scoliosis",
    "SegmentationAidedRegistration",
    "SegmentationReview",
    "SegmentRegistration",
    "ShapePopulationViewer",
    "ShapeRegressionExtension",
    "ShapeVariationAnalyzer",
    "SkullStripper",
    "SNRMeasurement",
    "SPHARM-PDM",
    "T1Mapping",
    "TCIABrowser",
    "ukftractography",
    "VASSTAlgorithms",
]

EXTENSION_NAME_CHECK_EXCEPTIONS = [
    # These extensions have name with "Slicer" prefix
    # (they were created before usage of this prefix was discouraged)
    "SlicerAIGT",
    "SlicerANTs",
    "SlicerANTsPy",
    "SlicerAutoscoperM",
    "SlicerBatchAnonymize",
    "SlicerBiomech",
    "SlicerCaseIterator",
    "SlicerCervicalSpine",
    "SlicerCineTrack",
    "SlicerCMF",
    "SlicerCochlea",
    "SlicerConda",
    "SlicerDcm2nii",
    "SlicerDentalModelSeg",
    "SlicerDevelopmentToolbox",
    "SlicerDiffusionComplexityMap",
    "SlicerDMRI",
    "SlicerElastix",
    "SlicerFab",
    "SlicerFreeSurfer",
    "SlicerHeadCTDeid",
    "SlicerHeart",
    "SlicerIGSIO",
    "SlicerIGT",
    "SlicerITKUltrasound",
    "SlicerJupyter",
    "SlicerLayoutButtons",
    "SlicerLiver",
    "SlicerLookingGlass",
    "SlicerMarkupConstraints",
    "SlicerMOOSE",
    "SlicerMorph",
    "SlicerMultiverSeg",
    "SlicerNetstim",
    "SlicerNeuro",
    "SlicerNeuropacs",
    "SlicerNeuroSegmentation",
    "SlicerOpenAnatomy",
    "SlicerOpenIGTLink",
    "SlicerOrbitSurgerySim",
    "SlicerPRISMRendering",
    "SlicerProstate",
    "SlicerProstateAblation",
    "SlicerPythonTestRunner",
    "SlicerRadiomics",
    "SlicerRT",
    "SlicerSOFA",
    "SlicerTelemetry",
    "SlicerThemes",
    "SlicerToKiwiExporter",
    "SlicerTractParcellation",
    "SlicerTrame",
    "SlicerVirtualMouseCursor",
    "SlicerVirtualReality",
    "SlicerVMTK",
]

LICENSE_CHECK_EXCEPTIONS = [
    "AirwaySegmentation",
    "AnatomyCarve",
    "AnglePlanesExtension",
    "Auto3dgm",
    "AutomatedDentalTools",
]

ACCEPTED_EXTENSION_CATEGORIES = [
    "Active Learning",
    "Analysis",
    "Auto3dgm",
    "BigImage",
    "Cardiac",
    "Chest Imaging Platform",
    "Conda",
    "Converters",
    "DICOM",
    "DSCI",
    "Developer Tools",
    "Diffusion",
    "Examples",
    "Exporter",
    "FTV Segmentation",
    "Filtering",
    "Filtering.Morphology",
    "Filtering.Vesselness",
    "Holographic Display",
    "Image Synthesis",
    "IGT",
    "Informatics",
    "Netstim",
    "Neuroimaging",
    "Nuclear Medicine",
    "Orthodontics",
    "Osteotomy Planning",
    "Otolaryngology",
    "Photogrammetry",
    "Pipelines",
    "Planning",
    "Printing",
    "Quantification",
    "Radiotherapy",
    "Registration",
    "Remote",
    "Rendering",
    "SPHARM",
    "Segmentation",
    "Sequences",
    "Shape Analysis",
    "Shape Regression",
    "Shape Visualization",
    "Simulation",
    "SlicerCMF",
    "SlicerMorph",
    "Spectral Imaging",
    "Supervisely",
    "Surface Models",
    "SurfaceLearner",
    "Tomographic Reconstruction",
    "Tracking",
    "Tractography",
    "Training",
    "Ultrasound",
    "Utilities",
    "Vascular Modeling Toolkit",
    "Virtual Reality",
    "VisSimTools",
    "Web System Tools",
    "Wizards",
]

if __name__ == "__main__":
    import sys
    sys.exit(main())
