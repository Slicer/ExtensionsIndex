#!/usr/bin/env python

"""
Python 3.x CLI for validating extension description files.
"""

import argparse
import os
import sys
import textwrap
import urllib.parse as urlparse

from functools import wraps


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


def parse_s4ext(ext_file_path):
    """Parse a Slicer extension description file.
    :param ext_file_path: Path to a Slicer extension description file.
    :return: Dictionary of extension metadata.
    """
    ext_metadata = {}
    with open(ext_file_path) as ext_file:
        for line in ext_file:
            if not line.strip() or line.startswith("#"):
                continue
            fields = [field.strip() for field in line.split(' ', 1)]
            assert(len(fields) <= 2)
            ext_metadata[fields[0]] = fields[1] if len(fields) == 2 else None
    return ext_metadata


@require_metadata_key("category")
def check_category(*_unused_args):
    pass


@require_metadata_key("contributors")
def check_contributors(*_unused_args):
    pass


@require_metadata_key("description")
def check_description(*_unused_args):
    pass


@require_metadata_key("homepage")
def check_homepage(extension_name, metadata):
    check_name = "check_homepage"
    homepage = metadata["homepage"]
    if not homepage.startswith("https://"):
        msg = f"homepage is `{homepage}` but it does not start with https"
        raise ExtensionCheckError(extension_name, check_name, msg)


@require_metadata_key("iconurl")
def check_iconurl(extension_name, metadata):
    check_name = "check_iconurl"
    iconurl = metadata["iconurl"]
    if not iconurl.startswith("https://"):
        msg = f"iconurl is '{iconurl}' but it does not start with https"
        raise ExtensionCheckError(extension_name, check_name, msg)


@require_metadata_key("screenshoturls", value_required=False)
def check_screenshoturls(extension_name, metadata):
    check_name = "check_screenshoturls"
    if metadata["screenshoturls"] is None:
        return
    for screenshoturl in metadata["screenshoturls"].split(" "):
        if not screenshoturl.startswith("http"):
            msg = f"screenshoturl is `{screenshoturl}` but it does not start with http"
            raise ExtensionCheckError(extension_name, check_name, msg)


@require_metadata_key("scmurl")
def check_scmurl_syntax(extension_name, metadata):
    check_name = "check_scmurl_syntax"

    if "://" not in metadata["scmurl"]:
        raise ExtensionCheckError(extension_name, check_name, "scmurl do not match scheme://host/path")

    supported_schemes = ["git", "https", "svn"]
    scheme = urlparse.urlsplit(metadata["scmurl"]).scheme
    if scheme not in supported_schemes:
        raise ExtensionCheckError(
            extension_name, check_name,
            "scmurl scheme is '%s' but it should by any of %s" % (scheme, supported_schemes))

@require_metadata_key("scm")
def check_scm_notlocal(extension_name, metadata):
    check_name = "check_scm_notlocal"
    if metadata["scm"] == "local":
        raise ExtensionCheckError(extension_name, check_name, "scm cannot be local")

@require_metadata_key("scmurl")
@require_metadata_key("scm")
def check_git_repository_name(extension_name, metadata):
    """See https://www.slicer.org/wiki/Documentation/Nightly/Developers/FAQ#Should_the_name_of_the_source_repository_match_the_name_of_the_extension_.3F
    """
    check_name = "check_git_repository_name"

    if metadata["scm"] != "git":
        return

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
        if not os.path.isfile(f):
            continue
        extension_name, extension = os.path.splitext(os.path.basename(filename))
        if extension != ".s4ext":
            continue
        available_extensions.append(extension_name)
        extension_description = parse_s4ext(f)
        if 'depends' not in extension_description:
            continue
        dependencies = extension_description['depends'].split(' ')
        for dependency in dependencies:
            if dependency == 'NA':
                # special value, just a placeholder that must be ignored
                continue
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
    parser.add_argument(
        "--check-git-repository-name", action="store_true",
        help="Check extension git repository name. Disabled by default.")
    parser.add_argument("-d", "--check-dependencies", help="Check all extension dsecription files in the provided folder.")
    parser.add_argument("/path/to/description.s4ext", nargs='*')
    args = parser.parse_args()

    checks = []

    if args.check_git_repository_name:
        checks.append(check_git_repository_name)

    if not checks:
        checks = [
            check_category,
            check_contributors,
            check_description,
            check_homepage,
            check_iconurl,
            check_scmurl_syntax,
            check_scm_notlocal,
            check_screenshoturls,
        ]

    total_failure_count = 0

    file_paths = getattr(args, "/path/to/description.s4ext")
    for file_path in file_paths:
        extension_name = os.path.splitext(os.path.basename(file_path))[0]

        failures = []

        metadata = parse_s4ext(file_path)
        for check in checks:
            try:
                check(extension_name, metadata)
            except ExtensionCheckError as exc:
                failures.append(str(exc))

        if failures:
            total_failure_count += len(failures)
            print("%s.s4ext" % extension_name)
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
