#!/usr/bin/env python

"""
Python 3.x CLI for validating extension description files.
"""

import argparse
import os
import sys
import textwrap
import urllib.request
import urllib.parse as urlparse

from functools import wraps
from http.client import HTTPException
from socket import timeout as SocketTimeout

try:
    from retry import retry
except ImportError:
    raise SystemExit(
        "retry not available: "
        "consider installing it running 'pip install retry'"
    ) from None


class ExtensionCheckError(RuntimeError):
    """Exception raised when a particular extension check failed.
    """
    def __init__(self, extension_name, check_name, details):
        self.extension_name = extension_name
        self.check_name = check_name
        self.details = details

    def __str__(self):
        return self.details


def check_url(url, timeout=1):

    @retry(TimeoutError, tries=3, delay=1, jitter=1, max_delay=3)
    def _check_url():
        opener = urllib.request.build_opener()
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        return opener.open(url, timeout=timeout).getcode(), None
    try:
        return _check_url()
    except urllib.request.HTTPError as exc:
        return exc.code, str(exc)
    except (TimeoutError, urllib.request.URLError, SocketTimeout) as exc:
        return -1, str(exc)
    except HTTPException as exc:
        return -2, str(exc)


def check_metadata_url(extension_name, metadata_key, url):
    check_name = "check_metadata_url"

    code, error = check_url(url)
    if code != 200:
        msg = f"{metadata_key} is '{url}': {error}"
        raise ExtensionCheckError(extension_name, check_name, msg)


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
def check_homepage(extension_name, metadata, check_url_reachable=False):
    check_name = "check_homepage"
    homepage = metadata["homepage"]
    if not homepage.startswith("https://"):
        msg = f"homepage is `{homepage}` but it does not start with https"
        raise ExtensionCheckError(extension_name, check_name, msg)

    if check_url_reachable:
        check_metadata_url(extension_name, "homepage", homepage)


@require_metadata_key("iconurl")
def check_iconurl(extension_name, metadata, check_url_reachable=False):
    check_name = "check_iconurl"
    iconurl = metadata["iconurl"]
    if not iconurl.startswith("https://"):
        msg = f"iconurl is '{iconurl}' but it does not start with https"
        raise ExtensionCheckError(extension_name, check_name, msg)

    if check_url_reachable:
        check_metadata_url(extension_name, "iconurl", iconurl)


@require_metadata_key("screenshoturls", value_required=False)
def check_screenshoturls(extension_name, metadata, check_url_reachable=False):
    check_name = "check_screenshoturls"
    if metadata["screenshoturls"] is None:
        return
    for index, screenshoturl in enumerate(metadata["screenshoturls"].split(" ")):
        if not screenshoturl.startswith("https://"):
            msg = f"screenshoturl[{index}] is `{screenshoturl}` but it does not start with https"
            raise ExtensionCheckError(extension_name, check_name, msg)

        if check_url_reachable:
            check_metadata_url(extension_name, f"screenshoturl[{index}]", screenshoturl)


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
    parser.add_argument(
        "--check-urls-reachable", action="store_true",
        help="Check homepage, iconurl and screenshoturls are reachable. Disabled by default.")
    parser.add_argument("-d", "--check-dependencies", help="Check all extension dsecription files in the provided folder.")
    parser.add_argument("/path/to/description.s4ext", nargs='*')
    args = parser.parse_args()

    checks = []

    if args.check_git_repository_name:
        checks.append((check_git_repository_name, {}))

    if not checks:
        checks = [
            (check_category, {}),
            (check_contributors, {}),
            (check_description, {}),
            (check_homepage, {"check_url_reachable": args.check_urls_reachable}),
            (check_iconurl, {"check_url_reachable": args.check_urls_reachable}),
            (check_scmurl_syntax, {}),
            (check_scm_notlocal, {}),
            (check_screenshoturls, {"check_url_reachable": args.check_urls_reachable}),
        ]

    def _check_extension(file_path):
        extension_name = os.path.splitext(os.path.basename(file_path))[0]

        failures = []

        metadata = parse_s4ext(file_path)
        for check, check_kwargs in checks:
            try:
                check(extension_name, metadata, **check_kwargs)
            except ExtensionCheckError as exc:
                failures.append(str(exc))

        # Keep track extension errors removing duplicates
        return extension_name, list(set(failures))

    extension_failures = {}
    file_paths = getattr(args, "/path/to/description.s4ext")
    for file_path in file_paths:
        extension_name, failures = _check_extension(file_path)
        extension_failures[extension_name] = failures

    total_failure_count = 0

    for extension_name, failures in extension_failures.items():
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
