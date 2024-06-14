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

| Date       | Extension Name                | Deprecation reason  |
|------------|-------------------------------|---------------------|
| 2024-06-14 | iGyne                         | Unmaintained and incompatible with Slicer >- 5.2 due to its dependencies to the Annotations module. |
| 2023-08-11 | mpReview                      | The extension is available again (it has been updated to use Segment Editor module instead of the removed Editor module). |
| 2023-07-13 | SegmentGeometry               | Extension was [renamed to SlicerBiomech](https://github.com/Slicer/ExtensionsIndex/commit/b72fefc948e9710af3c631acd42360699211f8e4)]. |
| 2022-03-29 | DeepInfer                     | Not updated for Python3. MONAILabel may be used instead. |
| 2022-03-26 | WASP                          | Extension was [not compatible with Python3](https://github.com/Tomnl/Slicer-Wasp/issues/2) and ITK watershed segmentation is already available in SegmentEditorExtraEffects extension (with the limtiation that it does not precompute multiple levels). |
| 2022-03-25 | LongitudinalPETCT             | Extension build was failing due to dependency on removed module (Annotations, Editor, Charts)(https://github.com/QIICR/LongitudinalPETCT/issues/17). |
| 2022-03-25 | MFSDA                         | Extension build was failing and [maintaners not responding](https://github.com/DCBIA-OrthoLab/MFSDA_Python/issues/26). |
| 2022-03-25 | ResampleDTIlogEuclidean       | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/NIRALUser/ResampleDTIlogEuclidean/issues/4). |
| 2022-03-25 | CBC_3D_I2MConversion          | Extension build was failing and not fixed for several years. |
| 2022-03-25 | MABMIS                        | Extension build was failing and not fixed for several years. |
| 2022-03-25 | exStone                       | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/qimo601/exStone/pull/2). |
| 2022-03-25 | SlicerAstro                   | Extension build was failing and [not fixed for a long time](https://github.com/Punzo/SlicerAstro/issues/116). |
| 2022-03-25 | GraphCutSegment               | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/Slicer/SlicerGraphCutSegment/pull/5). Probably "Grow from seeds" effect in Segment Editor produces better results. |
| 2022-03-25 | LAScarSegmenter               | Extension build was failing and [not fixed for a long time](https://github.com/ljzhu/LAScarSegmenter/issues/1). |
| 2022-03-25 | LASegmenter                   | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/ljzhu/LASegmenter/pull/8). |
| 2022-03-25 | ROBEXBrainExtraction          | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/CSIM-Toolkits/ROBEXBrainExtraction/pull/2). HDBrainExtraction or SwissSkullStripper extensions can be used instead. |
| 2022-03-25 | LesionSimulator               | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/CSIM-Toolkits/Slicer-LesionSimulatorExtension/pull/14). |
| 2022-03-25 | LesionSpotlight               | Extension build was failing and [maintaners not merging the proposed fix](https://github.com/CSIM-Toolkits/LesionSpotlightExtension/pull/7). |
| 2022-03-24 | SlicerOpenCV                  | Extension build was failing and [not fixed for a long time](https://github.com/Slicer/SlicerOpenCV/issues/74). OpenCV is now available using pip, so the extension may not be needed anymore. |
| 2022-03-24 | SlicerPinholeCameras          | Extension build was failing and [not fixed for a long time](https://github.com/VASST/SlicerPinholeCameras/issues/6). Requires OpenCV. |
| 2022-03-24 | OpenCVExample                 | Extension build was failing and not fixed for a long time. Requires OpenCV. |
| 2022-03-24 | SlicerVASST                   | Extension build was failing and [not fixed for a long time](https://github.com/VASST/SlicerVASST/issues/16). Requires OpenCV. |
| 2022-03-24 | MarginCalculator              | Extension build was failing and [not fixed for several years](https://github.com/jcfr/MarginCalculator/issues/1). SlicerRT extension offers related features, which can be further automated and extended using Python scripting to achieve similar features as this extension offered. |
| 2022-03-22 | IASEM                         | Extension build was failing and [not fixed for several years](https://github.com/blowekamp/Slicer-IASEM/pull/6). Most modules have alternatives (Segment Editor, Segment Statistics), and more sophisticated solutions now for dealing with very large images (e.g. using multi-resolution tiles). |
| 2022-03-22 | FiberViewerLight              | Extension build was failing and [not fixed for several years](https://github.com/NIRALUser/FiberViewerLight/issues/3). SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIProcess                    | Extension build was failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIPrep                       | Extension build was failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTI-Reg                       | Extension build was failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIAtlasFiberAnalyzer         | Extension build was failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | DTIAtlasBuilder               | Extension build was failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | ABC                           | Extension build was failing and not fixed for several years. SlicerDMRI extension has related features that might be used instead. |
| 2022-03-22 | SlicerPathology               | Extension build was failing and [not fixed for several years](https://github.com/SBU-BMI/SlicerPathology/issues/103). More generic tools, such as Segment Editor module or MONAI Label extension can be used for pathology image segmentation. |
| 2022-03-22 | AutoTract                     | Extension build was failing at submission and [got no response from maintainers](https://github.com/NIRALUser/AutoTract/issues/8). SlicerDMRI extension has tractography features that might be used instead. |
| 2022-03-17 | FacetedVisualizer             | Extension build was failing and [not fixed for several years](https://github.com/millerjv/FacetedVisualizer/issues/12). OpenAnatomy project has a similar web-based tool. |
| 2022-03-17 | LightWeightRobotIGT           | Extension build was failing and [not fixed for several years](https://github.com/SNRLab/LightWeightRobotIGT/issues/5). [ROS-IGTL bridge](https://github.com/openigtlink/ROS-IGTL-Bridge) can be used for interfacing the KUKA LWR robot with Slicer. |
| 2022-03-16 | VirtualFractureReconstruction | Extension build was failing and [not fixed for several years](https://github.com/kfritscher/VirtualFractureReconstructionSlicerExtension/pull/3). |
| 2022-03-16 | Cardiac_MRI_Toolkit           | Extension build was failing and [not fixed for several years](https://github.com/carma-center/carma_slicer_extension/issues/5). Segment Editor contains similar segmentation tools. |
| 2022-03-16 | Eigen                         | Not used anymore in by any extensions. Eigen is already available in ITK and VTK. |
| 2022-03-16 | DiceComputation               | Extension build was failing at submission and was [not fixed for several years](https://github.com/lchauvin/DiceComputation/pull/4). Dice score can be computed using Segment Comparison module in SlicerRT extension. |
| 2022-03-16 | RSSExtension                  | Extension build was failing at submission and was [not fixed for several years](https://github.com/gaoyi/RSSExtension/pull/9). Instead of robust statistics segmenter, "Grow from seeds" effect can be used in Segment Editor module. |
| 2022-03-16 | SupervisedSegmentation        | Extension build was failing at submission and was [not fixed for several years](https://github.com/chalupaDaniel/SlicerSupervisedSegmentation/issues/2). |
| 2022-03-16 | MultiLevelRegistration        | Extension build was failing at submission and was not fixed for several years. Since then SlicerElastix and SlicerANTs extensions were added that can be used for automatic image registration. |
| 2022-02-04 | SegmentationWizard            | Extension build was [not fixed for over two years](https://github.com/QTIM-Lab/SlicerSegmentationWizard/issues/1) and only offering features that are also available with Slicer core modules. |
| 2021-12-21 | SliceTracker                  | Relied on the now removed mpReview. |
| 2021-12-21 | mpReview                      | Relied on the now removed Editor. |
| 2020-12-13 | WindowLevelEffect.s4ext       | Moved into Slicer core (window/level mouse mode). |
| 2020-05-06 | CardiacAgatstonMeasures       | Project no longer active, requires Slicer 4.9 or less features, new developer needed. |
| 2020-04-18 | Sequences                     | Moved into Slicer core. |
| 2018-11-05 | FastGrowCutEffect             | The tool has been greatly improved and moved into the Segment editor. This old extension has not been maintained and failed to build. |
| 2017-10-16 | FinslerTractography           | Based on old and obsolete code. Improved version available as a standalone tool in https://github.com/tomdelahaije/fcm. |
| 2017-09-22 | SobolevSegmenter              | Unmaintained. This was a technology demo that was never completed. |
| 2017-08-25 | boost                         | Unmaintained and unused extension that fail to build. |
| 2017-04-24 | Multi-LevelRegistration       | Unmaintained and failed to build on macOS. |
| 2016-11-26 | Reporting                     | Renamed to QuantitativeReporting. |
| 2016-06-06 | ThingiverseBrowser            | Qt web browser API changed, which would have required significant refactoring of the extension. |
| 2016-04-09 | LumpNav                       | Unlist `LumpNav` extension from the extension manager. |
| 2015-09-11 | T1_Mapping                    | Replaced by new extension `T1Mapping`. |
| 2015-05-18 | TrackerStabilizer             | Replaced by new extension `Slicer-TrackerStabilizer`. |
| 2015-03-28 | MultidimData                  | Renamed to `Sequences`. |
| 2015-01-09 | houghTransformCLI             | Unmaintained and unused (iGyne on standby). It needs to be updated to be compatible with VTK6. |
| 2014-05-13 | VMTKSlicerExtension           | Renamed to SlicerVMTK. |
| 2014-04-17 | TransformVisualizer           | Moved to Slicer core. |
| 2014-04-09 | PlusRemote                    | Moved under `SlicerIGT` extension. |
| 2014-01-30 | KSlice                        | Replaced by `CarreraSlice`. |
| 2013-12-17 | DataStore                     | Moved to Slicer core as a RemoteModule. |
| 2013-12-05 | PathPlanner                   | Superseded by `PathExplorer` extension. |
| 2013-12-05 | VisuaLine                     | Superseded by `PathExplorer` extension. |
| 2013-11-06 | JsonCpp                       | Removed because it was used only by`TubeTK` dependency. Later moved to Slicer core. |
| 2013-11-06 | TubeTk                        | Removed waiting build issues are resolved. |
| 2013-10-23 | iGynePy                       | Removed because source code not available anymore. |
| 2013-05-08 | VolumeResliceDriver           | Moved under `SlicerIGT` extension. |
| 2012-10-24 | SpatialObjects                | Removed because `TubeTK` will be added and will provide the functionality. |
