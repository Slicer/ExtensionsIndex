Slicer Extensions Index
=======================

Overview
--------

Think of the ExtensionsIndex as a repository containing a list of [extension description file][]s 
(*.s4ext) used by the [Slicer][] [extensions build system][] to build, test, package and upload 
[extension][]s on an [extensions server][].

Once uploaded on an [extensions server][], within Slicer, [extension][]s can be [installed](http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/SlicerApplication/ExtensionsManager#Installing_an_extension) using the [extensions manager][].

An [extensions catalog][] provides Slicer users with a convenient way to access the [extension][]s
previously uploaded on the [extensions server][]:

* from within Slicer with the help of the [extensions manager][]
* from the web: http://slicer.kitware.com/midas3/slicerappstore

The rest of this document will provide the developer with detailed documentation, step-by-step 
instruction and also examples allowing to successfully test, package and upload [extension][]s.

The following diagram depicts how [extensions catalog][], [extensions server][], [CDash][] and the 
slicer factory interact.

<img width="80%" src="http://www.slicer.org/slicerWiki/images/a/ab/Extensions-Index-to-Catalog-cycle.png"/>

Contributing
------------

### Extension description files

To contribute an extension description file, consider the following check list:

1. Extension belongs to `Category 1` or `Category 2` as described in [Slicer requirements](http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/Extensions/CatalogPolicies)
2. [Set up an account on the extension server and obtain an API key][extensions-server-api-key-setup]
3. Extension has been built and tested on the following platform: Linux, MacOSX and Windows. You could for example do an `ExperimentalUpload` and make sure the extension can be installed successfully. See [manual build](#manual-build)
4. [Fork][] ExtensionIndex
5. Create an issue on [Slicer/ExtensionsIndex tracker][] (). Issue title should be `<ExtensionName> - Add extension`, issue description should provide details about the extension
6. Clone your fork, then create a topic named `<IssueNumber>-add-<ExtensionName>`
  
  ```
  git clone git@github.com:<yourlogin>/ExtensionsIndex SlicerExtensionsIndex
  cd SlicerExtensionsIndex
  git checkout -b <IssueNumber>-add-<ExtensionName>
  ```
  
7. Commit your description file. Commit title should be `Add <ExtensionName> extension` and the the issue number should be reference adding `See issue #<issuenumber>` at the end of the commit message.
8. Push the topic to your fork and Slicer folks will be automatically notified
9. That's it !

Remarks:

* `<IssueNumber>` and `<ExtensionName>` should be replaced with their actual value.


To contribute fixes associated to your extension, consider the following check list:

TBD 

### Dashboard submissions

Submission of experimental builds are welcome. See [manual build](#manual-build) instructions.

Submission of either continuous or nightly builds of extensions on Slicer [CDash][] 
should be done solely by the slicer factory machine maintained by Kitware folks. 
While nothing prevent such submission from happening, it won't be possible to upload extensions
on the [extensions server][] without the appropriate credentials.

Prerequisites
-------------

* [Slicer][] build tree >= 4.1.1 - [r20313](http://viewvc.slicer.org/viewvc.cgi/Slicer4?view=revision&revision=20313) - See [slicer build instruction][]

Extensions build system
----------------------
The extensions build system allows to drive the build, test, packaging and upload of slicer 
extensions. 

Using the [extensions build system source code][] living in the 
Slicer source tree, it is possible to build extensions using two different approaches:

1. [Manual build](#manual-build)
2. [Dashboard driven build](#dashboard-driven-build)

### Manual build

Relying on manual build provides a convenient way to:

* check [extension description file][]s are valid
* upload one or more extensions once to check that Slicer can download and install them

Given a directory containing one or more [extension description file][]s, it is possible to manually 
configure and build the associated [extension][]s specifying the following CMake options:

<table>
  <tr>
    <td><code>Slicer_DIR</code></td>
    <td>Path to Slicer build tree</td>
  </tr>
  <tr>
    <td><code>Slicer_EXTENSION_DESCRIPTION_DIR</code></td>
    <td>Path to folder containing <a href="#extension-description-file">extension description file</a>s</td>
  </tr>
</table>

Optionally, it is also possible to specify:

<table>
  <tr>
    <td><code><a href="http://www.cmake.org/cmake/help/v2.8.8/cmake.html#variable:CMAKE_BUILD_TYPE">CMAKE_BUILD_TYPE</a></code></td>
    <td>On unix-like platform, should match the build type of the associated Slicer build directory</td>
  </tr>
  <tr>
    <td><code>Slicer_UPLOAD_EXTENSIONS</code></td>
    <td>By default set to <code>OFF</code>.<br>If enabled, extension builds will be submitted to Slicer dashboard and associated packages will be uploaded to extensions server</td>
  </tr>
  <tr>
    <td><code>MIDAS_PACKAGE_URL</code></td>
    <td>MIDAS <a href="#extensions-server">extensions server</a> url specifying where the extension should be uploaded. For example http://slicer.kitware.com/midas3</td>
  </tr>
  <tr>
    <td><code>MIDAS_PACKAGE_EMAIL</code></td>
    <td>Email allowing to authenticate to the <a href="#extension-server">extensions server.</a></td>
  </tr>
  <tr>
    <td><code>MIDAS_PACKAGE_API_KEY</code></td>
    <td>Token allowing to <a href="#setting-up-an-account-and-obtaining-an-api-key">authenticate</a> to the <a href="#extension-server">extensions server</a>.</td>
  </tr>
</table>

#### Examples

The following examples are specific to unix-like platforms and can easily be adapted for windows.

##### Build your own set of extensions against Slicer trunk build tree

Considering the following assumptions:

1. Folder `SlicerExtensionsCustomIndex` contains the [extension description file][]s of your choice
2. Slicer trunk has been checkout into `/path/to/Slicer-master` and built into `/path/to/Slicer-master-SuperBuild-Release`
3. To upload extension(s) on the [extensions server][], an [API key][extensions-server-api-key-setup] has been obtained.

The associated extensions could be built doing:

<pre>
$ ls SlicerExtensionsCustomIndex
foo.s4ext
bar.s4ext
$ mkdir SlicerExtensionsCustomIndex-build
$ cd SlicerExtensionsCustomIndex-build
$ cmake -DSlicer_DIR:PATH=/path/to/Slicer-master-SuperBuild-Release/Slicer-build \
 -DSlicer_EXTENSION_DESCRIPTION_DIR:PATH=/path/to/SlicerExtensionsCustomIndex \
 -DCMAKE_BUILD_TYPE:STRING=Release \
 /path/to/Slicer-master/Extensions/CMake
$ make
</pre>

Then, to submit the configure/build/test results on [CDash](http://slicer.cdash.org/index.php?project=Slicer4#Extensions-Experimental) `Extensions-Experimental` track
and upload the extension on the [extensions server][] of your choice, 
there are two options:

1. [Build the target `ExperimentalUpload` associated with each extensions](#extension-build-test-package-and-upload-using-experimentalupload-target)
2. [Configure (or re-configure) the project passing the options `Slicer_UPLOAD_EXTENSIONS`, 
`MIDAS_PACKAGE_URL`, `MIDAS_PACKAGE_EMAIL` and `MIDAS_PACKAGE_API_KEY`](#extensions-build-test-package-and-upload-using-slicer_upload_extensions-option)


###### Extension build, test, package and upload using `ExperimentalUpload` target

<pre>
$ cd SlicerExtensionsCustomIndex-build
$ cd foo-build
$ cmake -DMIDAS_PACKAGE_URL:STRING=http://slicer.kitware.com/midas3 \
 -DMIDAS_PACKAGE_EMAIL:STRING=jchris.fillionr@kitware.com \
 -DMIDAS_PACKAGE_API_KEY:STRING=a0b012c0123d012abc01234a012345a0 .
$ make ExperimentalUpload
</pre>

<img width="70%" src="http://www.slicer.org/slicerWiki/images/7/74/SlicerExtensionsCustomIndex-CDash-Foo-Extension-ExperimentalUpload.png"/>

<img width="70%" src="http://www.slicer.org/slicerWiki/images/f/f4/SlicerExtensionsCustomIndex-CDash-foo-download-link.png"/>

To simply submit the configure/build/test results on CDash skipping the upload part, building target `Experimental` 
is sufficient. This is expected to work only for Slicer >= 4.1.2. See issue [#2166](http://www.na-mic.org/Bug/view.php?id=2166)

<pre>
$ cd SlicerExtensionsCustomIndex-build
$ cd foo-build
$ make Experimental
</pre>

<img width="70%" src="http://www.slicer.org/slicerWiki/images/4/45/SlicerExtensionsCustomIndex-CDash-Foo-Extension-Experimental.png"/>


###### Extensions build, test, package and upload using `Slicer_UPLOAD_EXTENSIONS` option

<pre>
$ cd SlicerExtensionsCustomIndex-build
$ cmake -DSlicer_DIR:PATH=/path/to/Slicer-master-SuperBuild-Release/Slicer-build \
 -DSlicer_EXTENSION_DESCRIPTION_DIR:PATH=/path/to/SlicerExtensionsCustomIndex \
 -DCMAKE_BUILD_TYPE:STRING=Release \
 -DSlicer_UPLOAD_EXTENSIONS:BOOL=ON \
 -DMIDAS_PACKAGE_URL:STRING=http://slicer.kitware.com/midas3 \
 -DMIDAS_PACKAGE_EMAIL:STRING=jchris.fillionr@kitware.com \
 -DMIDAS_PACKAGE_API_KEY:STRING=a0b012c0123d012abc01234a012345a0 \
 /path/to/Slicer-master/Extensions/CMake
</pre>

##### Build your own set of extensions against Slicer 4.1.1 build tree

Considering the following assumptions:

1. Folder `SlicerExtensionsCustomIndex` contains the [extension description file][]s of your choice
2. Slicer 4.1.1 has been checkout into `/path/to/Slicer-411` and built into `/path/to/Slicer-411-SuperBuild-Release`
3. To upload extension(s) on the [extensions server][], an [API key][extensions-server-api-key-setup] has been obtained.

The associated extensions could be built following the instruction listed in the previous section 
and changing occurences of `Slicer-master` into `Slicer-411`.

##### Build slicer extensions associated with Slicer trunk

Considering the following assumption:

1. Slicer trunk has been checkout into `/path/to/Slicer-master` and built into `/path/to/Slicer-master-SuperBuild-Release`

The associated extensions could be built doing:

<pre>
$ git clone git://github.com/Slicer/ExtensionsIndex.git SlicerExtensionsIndex-master
$ mkdir SlicerExtensionsIndex-master-build
$ cd SlicerExtensionsIndex-master-build
$ cmake -DSlicer_DIR:PATH=/path/to/Slicer-master-SuperBuild-Release/Slicer-build \
 -DSlicer_EXTENSION_DESCRIPTION_DIR:PATH=/path/to/SlicerExtensionsIndex-master \
 -DCMAKE_BUILD_TYPE:STRING=Release \
 /path/to/Slicer-master/Extensions/CMake
$ make
</pre>

##### Build slicer extensions associated with Slicer 4.1.1

Considering the following assumption:

1. Slicer trunk has been checkout into `/path/to/Slicer-411` and built into `/path/to/Slicer-411-SuperBuild-Release`

The associated extensions could be built doing:

<pre>
$ git clone git://github.com/Slicer/ExtensionsIndex.git -b 4.1.1 SlicerExtensionsIndex-411
$ mkdir SlicerExtensionsIndex-411-build
$ cd SlicerExtensionsIndex-411-build
$ cmake -DSlicer_DIR:PATH=/path/to/Slicer-411-SuperBuild-Release/Slicer-build \
 -DSlicer_EXTENSION_DESCRIPTION_DIR:PATH=/path/to/SlicerExtensionsIndex-411 \
 -DCMAKE_BUILD_TYPE:STRING=Release \
 /path/to/Slicer-411/Extensions/CMake
$ make
</pre>


### Dashboard driven build

Continuous and nightly extension dashboards are setup on the slicer factory machine 
maintained by [Kitware](http://www.kitware.com) folks. Assuming you install your own 
[extensions server][], you could also distribute  your own set of extensions.

* Setting both nightly and continuous builds of the extensions is a key component of the Slicer 
continuous integration process. 

* By customizing the [extension template dashboard script][], it is possible to easily 
setup dashboard client submitting to [CDash][].

* The images reported below illustrate the dashboard submissions associated with the continuous 
and nightly builds of Slicer extensions associated to both Slicer trunk and Slicer 4.1.1.

<img width="70%" src="http://www.slicer.org/slicerWiki/images/3/39/Slicer-411-Extensions-build-system-nightly.png"/>
<img width="70%" src="http://www.slicer.org/slicerWiki/images/f/f3/Slicer-411-Extensions-build-system-continuous.png"/>
<img width="70%" src="http://www.slicer.org/slicerWiki/images/1/17/Slicer-Extensions-build-system-nightly.png"/>
<img width="70%" src="http://www.slicer.org/slicerWiki/images/5/52/Slicer-Extensions-build-system-continuous.png"/>

Extension description file
----------------------------

See https://github.com/Slicer/ExtensionsIndex/wiki/Extension-description-file

Extension
---------

A extension bundles one or multiple [slicer modules](http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/Developers/Modules).

Extensions Catalog
------------------

* The extensions catalog provides Slicer users with a convenient web site allowing to browse, download 
and install available extensions:

 * from within Slicer with the help of the [extensions manager][]
 * from the web: http://slicer.kitware.com/midas3/slicerappstore

Extensions server
----------------

* An extensions server is a [MIDAS][] instance having the plugins <code>[slicerpackages][]</code>
 and <code>[slicerappstore][]</code> installed.

* Assuming you [install your own extensions server](#install-your-own-extensions-server), 
 it is possible to manage, serve and distribute extensions yourself. As depicted on the image below, 
 Slicer users will have to set a different extensions server 
 in `Edit -> Application Settings -> Extensions`.

![Slicer Extensions settings](http://www.slicer.org/slicerWiki/images/e/e4/Slicer-r20312-Extensions-Settings.png)

* The authoritative slicer extensions server is <http://slicer.kitware.com/midas3>

### Setting up an account and obtaining an API key

In order to upload extensions on the [slicer extensions server][], it is required to:

1. Create an account by [registering][slicer extensions server]

  <img width="70%" src="http://www.slicer.org/slicerWiki/images/7/7c/Slicer-midas-extensions-server-registration.png"/>

2. [Join the NA-MIC community](http://slicer.kitware.com/midas3/community/23)

3. Send an email on the [slicer developers list][] presenting your extension(s) and asking 
to be granted write permission on the [experimental folder](http://slicer.kitware.com/midas3/folder/253).

4. Then, you should be able to retrieve your API key looking at your account details. Note that 
any one of the API key associated with a given user account is valid. It's the user role to manage 
its keys.

<img width="70%" src="http://www.slicer.org/slicerWiki/images/3/34/Slicer-midas-extensions-server-obtaining-api-key.png"/>

### Install your own extensions server

To understand what are the steps required to install and manage your own extensions server, 
consider reading [MIDAS server installation instructions](http://www.kitware.com/midaswiki/index.php/Documentation/Latest/User/Introduction).

Make also sure to install and configure the plugins <code>[slicerpackages][]</code>
 and <code>[slicerappstore][]</code>.

Meta
----

* Code: `git clone git://github.com/Slicer/ExtensionsIndex.git`
* Bugs: <http://github.com/Slicer/ExtensionsIndex/issues>

License
-------

* [3D Slicer license](http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/License.txt?view=co)

[fork]: http://help.github.com/forking/
[Slicer/ExtensionsIndex tracker]: https://github.com/Slicer/ExtensionsIndex/issues

[CDash]: http://slicer.cdash.org/index.php?project=Slicer4

[midas]: http://www.midasplatform.org/
[slicerappstore]: https://github.com/midasplatform/slicerappstore
[slicerpackages]: https://github.com/midasplatform/slicerpackages

[slicer]: http://slicer.org
[slicer build instruction]: www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Developers/Build_Instructions
[slicer developers list]: http://massmail.bwh.harvard.edu/mailman/listinfo/slicer-devel
[slicer extensions server]: http://slicer.kitware.com

[extensions manager]: http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/SlicerApplication/ExtensionsManager

[extension description file]: #extension-description-file
[extension]: #extension
[extensions build system]: #extensions-build-system
[extensions catalog]: #extensions-catalog
[extensions server]: #extensions-server
[extensions build system source code]: https://github.com/Slicer/Slicer/tree/master/Extensions/CMake
[extension template dashboard script]: https://github.com/Slicer/Slicer/blob/master/Extensions/CMake/SlicerExtensionsDashboardScript.TEMPLATE.cmake

[extensions-server-api-key-setup]: #setting-up-an-account-and-obtaining-an-api-key

[descriptionfileexample]: https://github.com/Slicer/ExtensionsIndex/blob/master/SkullStripper.s4ext

