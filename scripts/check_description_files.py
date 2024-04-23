#!/usr/bin/env python

"""
Python 3.x CLI for validating extension description files.
"""

import argparse
import json
import os
import sys
import textwrap
import urllib.request
import urllib.parse as urlparse

from functools import wraps

try:
    from joblib import Parallel, delayed, parallel_backend
except ImportError:
    raise SystemExit(
        "retry not available: "
        "consider installing it running 'pip install joblib'"
    ) from None


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


def parse_json(ext_file_path):
    """Parse a Slicer extension description file.
    :param ext_file_path: Path to a Slicer extension description file (.json).
    :return: Dictionary of extension metadata.
    """
    with open(ext_file_path) as input_file:
        try:
            return json.load(input_file)
        except json.JSONDecodeError as exc:
            extension_name = os.path.splitext(os.path.basename(ext_file_path))[0]
            raise ExtensionParseError(
                extension_name,
                textwrap.dedent("""
                Failed to parse '%s': %s
                """ % (ext_file_path, exc)))


@require_metadata_key("category")
def check_category(*_unused_args):
    pass


@require_metadata_key("scmurl")
def check_scmurl_syntax(extension_name, metadata):
    check_name = "check_scmurl_syntax"

    if "://" not in metadata["scmurl"]:
        raise ExtensionCheckError(extension_name, check_name, "scmurl do not match scheme://host/path")

    supported_schemes = ["git", "https"]
    scheme = urlparse.urlsplit(metadata["scmurl"]).scheme
    if scheme not in supported_schemes:
        raise ExtensionCheckError(
            extension_name, check_name,
            "scmurl scheme is '%s' but it should by any of %s" % (scheme, supported_schemes))


@require_metadata_key("scmurl")
def check_git_repository_name(extension_name, metadata):
    """See https://www.slicer.org/wiki/Documentation/Nightly/Developers/FAQ#Should_the_name_of_the_source_repository_match_the_name_of_the_extension_.3F
    """
    check_name = "check_git_repository_name"

    repo_name = os.path.splitext(urlparse.urlsplit(metadata["scmurl"]).path.split("/")[-1])[0]

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
        if 'depends' not in extension_description:
            continue
        dependencies = extension_description['depends']
        for dependency in dependencies:
            if dependency in required_extensions:
                required_extensions[dependency].append(extension_name)
            else:
                required_extensions[dependency] = [extension_name]
    print(f"Checked dependency between {len(available_extensions)} extensions.")
    error_count = 0
    for extension in required_extensions:
        if extension in available_extensions:
            # required extension is found
            continue
        required_by_extensions = ', '.join(required_extensions[extension])
        print(f"{extension} extension is not found. It is required by extension: {required_by_extensions}.")
        error_count += 1
    return error_count


def main():
    parser = argparse.ArgumentParser(
        description='Validate extension description files.')
    parser.add_argument("-d", "--check-dependencies", help="Check all extension dsecription files in the provided folder.")
    parser.add_argument("/path/to/extension_name.json", nargs='*')
    args = parser.parse_args()

    checks = []

    if not checks:
        checks = [
            (check_category, {}),
            (check_git_repository_name, {}),
            (check_scmurl_syntax, {}),
        ]

    def _check_extension(file_path, verbose=False):
        extension_name = os.path.splitext(os.path.basename(file_path))[0]

        if verbose:
            print(f"Checking {extension_name}")

        failures = []

        try:
            metadata = parse_json(file_path)
        except ExtensionParseError as exc:
            failures.append(str(exc))

        if not failures:
            for check, check_kwargs in checks:
                try:
                    check(extension_name, metadata, **check_kwargs)
                except ExtensionCheckError as exc:
                    failures.append(str(exc))

        # Keep track extension errors removing duplicates
        return extension_name, list(set(failures))

    file_paths = getattr(args, "/path/to/extension_name.json")
    with parallel_backend("threading", n_jobs=6):
        jobs = Parallel(verbose=False)(
            delayed(_check_extension)(file_path)
            for file_path in file_paths
        )

    total_failure_count = 0

    for extension_name, failures in jobs:
        if failures:
            total_failure_count += len(failures)
            print("%s.json" % extension_name)
            for failure in set(failures):
                print("  %s" % failure)

    print(f"Checked content of {len(file_paths)} description files.")


    if args.check_dependencies:
        total_failure_count += check_dependencies(args.check_dependencies)

    print(f"Total errors found in extension descriptions: {total_failure_count}")
    sys.exit(total_failure_count)


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


if __name__ == "__main__":
    main()
