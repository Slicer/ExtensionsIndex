# ARCHIVE

The modules in this directory are not actively maintained. They
persist in this directory as a convenient marker for historical
documentation, and to provide a starting point if future
projects would like to resume development.

Removing unused modules from the primary directory reduces
burden on slicer developers.

A short list of reasons why a module may be placed into
the archive are as follows

- Project that originally funded the extension is now complete
- The extension has been superceeded with another, and is not recommended
- The extension has no development support, and no longer runs properly

# Optional extension documentation:

| Date       | Extension Name                | Commit                                                             | Deprecation reason  |
|------------|-------------------------------|--------------------------------------------------------------------|---------------------|
| 2022-03-24 | SlicerOpenCV                  |                                                                    | Removed due to the extension build failing and [not fixed for a long time](https://github.com/Slicer/SlicerOpenCV/issues/74). OpenCV is now available using pip, so the extension may not be needed anymore. |
| 2022-03-24 | SlicerPinholeCameras          |                                                                    | Removed due to the extension build failing and [not fixed for a long time](https://github.com/VASST/SlicerPinholeCameras/issues/6). Requires OpenCV. |
| 2022-03-24 | OpenCVExample                 |                                                                    | Removed due to the extension build failing and not fixed for a long time. Requires OpenCV. |
| 2022-03-24 | SlicerVASST                   |                                                                    | Removed due to the extension build failing and [not fixed for a long time](https://github.com/VASST/SlicerVASST/issues/16). Requires OpenCV. |
| 2022-03-24 | MarginCalculator              |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/jcfr/MarginCalculator/issues/1). SlicerRT extension offers related features, which can be further automated and extended using Python scripting to achieve similar features as this extension offered. |
| 2022-03-22 | IASEM                         |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/blowekamp/Slicer-IASEM/pull/6). Most modules have alternatives (Segment Editor, Segment Statistics), and more sophisticated solutions now for dealing with very large images (e.g. using multi-resolution tiles). |
| 2022-03-22 | FiberViewerLight              |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/NIRALUser/FiberViewerLight/issues/3). SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIProcess                    |                                                                    | Removed due to the extension build failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIPrep                       |                                                                    | Removed due to the extension build failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTI-Reg                       |                                                                    | Removed due to the extension build failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIAtlasFiberAnalyzer         |                                                                    | Removed due to the extension build failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIAtlasBuilder               |                                                                    | Removed due to the extension build failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | ABC                           |                                                                    | Removed due to the extension build failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | SlicerPathology               |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/SBU-BMI/SlicerPathology/issues/103). More generic tools, such as Segment Editor module or MONAI Label extension can be used for pathology image segmentation. |
| 2022-03-22 | AutoTract                     |                                                                    | Removed due to the extension build failing at submission and [got no response from maintainers](https://github.com/NIRALUser/AutoTract/issues/8). SlicerDMRI extension has tractography features that might be used instead. |
| 2022-03-17 | FacetedVisualizer             |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/millerjv/FacetedVisualizer/issues/12). OpenAnatomy project has a similar web-based tool. |
| 2022-03-17 | LightWeightRobotIGT           |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/SNRLab/LightWeightRobotIGT/issues/5). [ROS-IGTL bridge](https://github.com/openigtlink/ROS-IGTL-Bridge) can be used for interfacing the KUKA LWR robot with Slicer. |
| 2022-03-16 | VirtualFractureReconstruction |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/kfritscher/VirtualFractureReconstructionSlicerExtension/pull/3). |
| 2022-03-16 | Cardiac_MRI_Toolkit           |                                                                    | Removed due to the extension build failing and [not fixed for several years](https://github.com/carma-center/carma_slicer_extension/issues/5). Segment Editor contains similar segmentation tools. |
| 2022-03-16 | Eigen                         |                                                                    | Not used anymore in by any extensions. Eigen is already available in ITK and VTK. |
| 2022-03-16 | DiceComputation               |                                                                    | Removed due to the extension build failing at submission and was [not fixed for several years](https://github.com/lchauvin/DiceComputation/pull/4). Dice score can be computed using Segment Comparison module in SlicerRT extension. |
| 2022-03-16 | RSSExtension                  |                                                                    | Removed due to the extension build failing at submission and was [not fixed for several years](https://github.com/gaoyi/RSSExtension/pull/9). Instead of robust statistics segmenter, "Grow from seeds" effect can be used in Segment Editor module. |
| 2022-03-16 | SupervisedSegmentation        |                                                                    | Removed due to the extension build failing at submission and was [not fixed for several years](https://github.com/chalupaDaniel/SlicerSupervisedSegmentation/issues/2). |
| 2022-03-16 | MultiLevelRegistration        |                                                                    | Removed due to the extension build failing at submission and was not fixed for several years. Since then SlicerElastix and SlicerANTs extensions were added that can be used for automatic image registration. |
| 2022-02-04 | SegmentationWizard            |                                                                    | Removed due to the extension [not fixed for over two years](https://github.com/QTIM-Lab/SlicerSegmentationWizard/issues/1) and only offering features that are also available with Slicer core modules. |
| 2021-12-21 | SliceTracker                  | [4df1f21](https://github.com/Slicer/ExtensionsIndex/commit/4df1f21)| Removed due to reliance on the now removed mpReview. |
| 2021-12-21 | mpReview                      | [1c43bd7](https://github.com/Slicer/ExtensionsIndex/commit/1c43bd7)| Removed due to reliance on the now removed Editor. |
| 2020-12-13 | WindowLevelEffect.s4ext       |                                                                    | Moved into Slicer core (window/level mouse mode). |
| 2020-05-06 | CardiacAgatstonMeasures       | [5418df1](https://github.com/Slicer/ExtensionsIndex/commit/5418df1)| Project no longer active, requires Slicer 4.9 or less features, new developer needed. |
| 2020-04-18 | Sequences                     | [f9cd072](https://github.com/Slicer/ExtensionsIndex/commit/f9cd072)| Moved into Slicer core. |
| 2018-11-05 | FastGrowCutEffect             | [041d4a0](https://github.com/Slicer/ExtensionsIndex/commit/041d4a0)| The tool has been greatly improved and moved into the Segment editor. This old extension has not been maintained and failed to build. |
| 2017-10-16 | FinslerTractography           | [d9b3f5d](https://github.com/Slicer/ExtensionsIndex/commit/d9b3f5d)| Based on old and obsolete code. Improved version available as a standalone tool in https://github.com/tomdelahaije/fcm. |
| 2017-09-22 | SobolevSegmenter              | [e7cd3c3](https://github.com/Slicer/ExtensionsIndex/commit/e7cd3c3)| Unmaintained. This was a technology demo that was never completed. |
| 2017-08-25 | boost                         | [6d42bfc](https://github.com/Slicer/ExtensionsIndex/commit/6d42bfc)| Unmaintained and unused extension that fail to build. |
| 2017-04-24 | Multi-LevelRegistration       | [7244bc2](https://github.com/Slicer/ExtensionsIndex/commit/7244bc2)| Unmaintained and failed to build on macOS. |
| 2016-11-26 | Reporting                     | [fbd4c46](https://github.com/Slicer/ExtensionsIndex/commit/fbd4c46)| Renamed to QuantitativeReporting. |
| 2016-06-06 | ThingiverseBrowser            | [9203d35](https://github.com/Slicer/ExtensionsIndex/commit/9203d35)| Remove broken `ThingiverseBrowser` extension. |
| 2016-04-09 | LumpNav                       | [eb85559](https://github.com/Slicer/ExtensionsIndex/commit/eb85559)| Unlist `LumpNav` extension from the extension manager. |
| 2015-09-11 | T1_Mapping                    | [cca373c](https://github.com/Slicer/ExtensionsIndex/commit/cca373c)| Replaced by new extension `T1Mapping`. |
| 2015-05-18 | TrackerStabilizer             | [ae51bca](https://github.com/Slicer/ExtensionsIndex/commit/ae51bca)| Replaced by new extension `Slicer-TrackerStabilizer`. |
| 2015-03-28 | MultidimData                  | [6aacb75](https://github.com/Slicer/ExtensionsIndex/commit/6aacb75)| Renamed to `Sequences`. |
| 2015-01-09 | houghTransformCLI             | [2592e8b](https://github.com/Slicer/ExtensionsIndex/commit/2592e8b)| Unmaintained and unused (iGyne on standby). It needs to be updated to be compatible with VTK6. |
| 2014-05-13 | VMTKSlicerExtension           | [4c3611a](https://github.com/Slicer/ExtensionsIndex/commit/4c3611a)| Renamed to SlicerVMTK. |
| 2014-04-17 | TransformVisualizer           | [2cdbcf5](https://github.com/Slicer/ExtensionsIndex/commit/2cdbcf5)| Moved to Slicer core. |
| 2014-04-09 | PlusRemote                    | [2cf7305](https://github.com/Slicer/ExtensionsIndex/commit/2cf7305)| Moved under `SlicerIGT` extension. |
| 2014-01-30 | KSlice                        | [58e8a12](https://github.com/Slicer/ExtensionsIndex/commit/58e8a12)| Replaced by `CarreraSlice`. |
| 2013-12-17 | DataStore                     | [b77e9d7](https://github.com/Slicer/ExtensionsIndex/commit/b77e9d7)| Moved to Slicer core as a RemoteModule. |
| 2013-12-05 | PathPlanner                   | [8e9015c](https://github.com/Slicer/ExtensionsIndex/commit/8e9015c)| Will be superseded by `PathXplorer` extension. |
| 2013-12-05 | VisuaLine                     | [8e9015c](https://github.com/Slicer/ExtensionsIndex/commit/8e9015c)| Will be superseded by `PathXplorer` extension. |
| 2013-11-06 | JsonCpp                       | [38e180b](https://github.com/Slicer/ExtensionsIndex/commit/38e180b)| Removed because it was used only by`TubeTK` dependency. Later moved to Slicer core. |
| 2013-11-06 | TubeTk                        | [38e180b](https://github.com/Slicer/ExtensionsIndex/commit/38e180b)| Removed waiting build issues are resolved. |
| 2013-10-23 | iGynePy                       | [96d3c5a](https://github.com/Slicer/ExtensionsIndex/commit/96d3c5a)| Removed because source code not available anymore. |
| 2013-05-08 | VolumeResliceDriver           | [2d26ca6](https://github.com/Slicer/ExtensionsIndex/commit/2d26ca6)| Moved under `SlicerIGT` extension. |
| 2012-10-24 | SpatialObjects                | [bae360c](https://github.com/Slicer/ExtensionsIndex/commit/bae360c)| Removed because `TubeTK` will be added and will provide the functionality. |
