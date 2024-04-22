<!--
Thank you for contributing to 3D Slicer!
- To add a new extension with this pull request: Please keep content of "New extension" section and put an 'x' in the brackets for each todo item to indicate that you have accomplished that prerequisite.
- To update an existing extension with this pull request: Please delete all text in this template and just describe which extension is updated and optionally tell us in a sentence what has been changed. To make extension updates easier in the future you may consider replacing specific git hash in your s4ext file by a branch name (for example: `main` for Slicer Preview Releases; `(majorVersion).(minorVersion)` such as `4.10` for Slicer Stable Releases).
-->

# New extension

<!-- To make sure users can find your extension, understand what it is intended for and how to use it, please complete the checklist below. You do not need to complete all the item by the time you submit the pull request, but most likely the changes will only be merged if all the tasks are done. See more information about the submission process here: https://slicer.readthedocs.io/en/latest/developer_guide/extensions.html -->

- [ ] Extension has a reasonable name (not too general, not too narrow, suggests what the extension is for)
- [ ] Repository name is Slicer+ExtensionName
- [ ] Repository is associated with `3d-slicer-extension` GitHub topic so that it is listed [here](https://github.com/topics/3d-slicer-extension). To edit topics, click the settings icon in the right side of "About" section header and enter `3d-slicer-extension` in "Topics" and click "Save changes". To learn more about topics, read https://help.github.com/en/articles/about-topics
- [ ] Extension description summarizes in 1-2 sentences what the extension is usable (should be understandable for non-experts)
- [ ] Any known related patents must be mentioned in the extension description.
- [ ] LICENSE.txt is present in the repository root. MIT  (https://choosealicense.com/licenses/mit/) or Apache (https://choosealicense.com/licenses/apache-2.0/) license is recommended. If source code license is more restrictive for users than MIT, BSD, Apache, or 3D Slicer license then the name of the used license must be mentioned in the extension description.
- [ ] Extension URL and revision (scmurl, scmrevision) is correct, consider using a branch name (main, release, ...) instead of a specific git hash to avoid re-submitting pull request whenever the extension is updated
- [ ] Extension icon URL is correct (do not use the icon's webpage but the raw data download URL that you get from the download button - it should look something like this: https://raw.githubusercontent.com/user/repo/main/SomeIcon.png)
- [ ] Screenshot URLs (screenshoturls) are correct, contains at least one
- [ ] Homepage URL points to valid webpage containing the following:
  - [ ] Extension name
  - [ ] Short description: 1-2 sentences, which summarizes what the extension is usable for
  - [ ] At least one nice, informative image, that illustrates what the extension can do. It may be a screenshot.
  - [ ] Description of contained modules: at one sentence for each module
  - [ ] Tutorial: step-by-step description of at least the most typical use case, include a few screenshots, provide download links to sample input data set
  - [ ] Publication: link to publication and/or to PubMed reference (if available)
  - [ ] License: We suggest you use a permissive license that includes patent and contribution clauses.  This will help protect developers and ensure the code remains freely available.  We suggest you use the [Slicer License](https://github.com/Slicer/Slicer/blob/main/License.txt) or the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Always mention in your README file the license you have chosen.  If you choose a different license, explain why to the extension maintainers. Depending on the license we may not be able to host your work. Read [here](https://opensource.guide/legal/#which-open-source-license-is-appropriate-for-my-project) to learn more about licenses.
  - [ ] Content of submitted s4ext file is consistent with the top-level CMakeLists.txt file in the repository (description, URLs, dependencies, etc. are the same)
- Hide unused features in the repository to reduce noise/irrelevant information:
  - [ ] Click `Settings` and in repository settings uncheck `Wiki`, `Projects`, and `Discussions` (if they are currently not used)
  - [ ] Click the settings icon next to `About` in the top-right corner of the repository main page and uncheck `Releases` and `Packages` (if they are currently not used)
<!-- If you have any questions or comments then please describe them here. -->
