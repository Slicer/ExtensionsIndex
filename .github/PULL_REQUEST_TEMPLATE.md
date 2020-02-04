Thank you for contributing to 3D Slicer!

- **To add a new extension with this pull request**: Please keep content of "TODO list for submitting a new extension" section and put an 'x' character in the brackets for each todo item to indicate that you have accomplished that prerequisite.

- **To update an existing extension with this pull request**: Please delete all text in this template and just describe which extension is updated and optionally tell us in a sentence what has been changed. To make extension updates easier in the future (so that you don't have to submit a new pull request after each change in your extension), you may consider replacing specific git hash in your s4ext file by a branch name (for example: `master` or `release` for nightly version; `(majorVersion).(minorVersion)` such as `4.10` for stable Slicer version).

# TODO list for submitting a new extension

[To make sure users can find your extension, understand what it is intended for and how to use it, please complete the checklist below. You do not need to complete all the item by the time you submit the pull request, but most likely the changes will only be merged if all the tasks are done. See more information about the submission process on the Slicer wiki: https://www.slicer.org/wiki/Documentation/Nightly/Developers/Tutorials/BuildTestPackageDistributeExtensions]

- [ ] Extension has a reasonable name (not too general, not too narrow, suggests what the extension is for)
- [ ] Repository name is Slicer+ExtensionName
- [ ] Repository is associated with `3d-slicer-extension` GitHub topic so that it is listed [here](https://github.com/topics/3d-slicer-extension). To learn more about topic, read https://help.github.com/en/articles/about-topics
- [ ] Extension description summarizes in 1-2 sentences what the extension is usable (should be understandable for non-experts)
- [ ] Extension URL and revision (scmurl, scmrevision) is correct, consider using a branch name (master, release, ...) instead of a specific git has to avoid re-submitting pull request whenever the extension is updated
- [ ] Extension icon URL is correct
- [ ] Screenshot URLs (screenshoturls) are correct, contains at least one
- [ ] Homepage URL points to valid webpage containing the following:
  - [ ] Extension name
  - [ ] Short description: 1-2 sentences, which summarizes what the extension is usable for
  - [ ] At least one nice, informative image, that illustrates what the extension can do. It may be a screenshot.
  - [ ] Description of contained modules: at one sentence for each module
  - [ ] Tutorial: step-by-step description of at least the most typical use case, include a few screenshots, provide download links to sample input data set
  - [ ] Publication: link to publication and/or to PubMed reference (if available)
  - [ ] License: We suggest you use a permissive license that includes patent and contribution clauses.  This will help protect developers and ensure the code remains freely available.  We suggest you use the [Slicer License](https://github.com/Slicer/Slicer/blob/master/License.txt) or the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Always mention in your README file the license you have chosen.  If you choose a different license, explain why to the extension maintainers. Depending on the license we may not be able to host your work.
Read [here](https://opensource.guide/legal/#which-open-source-license-is-appropriate-for-my-project) to learn more about licenses.

[If you have any questions or comments then please describe them here.]
