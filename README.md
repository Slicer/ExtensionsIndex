Slicer Extensions Index
=======================

Overview
--------

Think of the ExtensionsIndex as a repository containing a list of [extension description file][]s 
(*.s4ext) used by the [Slicer][] extensions build system to build, test, package and upload 
extensions on an [extensions server][].

Once uploaded on an [extensions server][], within Slicer, extensions can be installed using the [extensions manager][].

An [extensions catalog][] provides Slicer users with a convenient way to access the extensions
previously uploaded on the [extensions server][]:

* from within Slicer with the help of the [extensions manager][]
* from the web: http://slicer.kitware.com/midas3/slicerappstore

The following diagram depicts how [extensions catalog][], [extensions server][], [CDash][] and the 
slicer factory interact.

<img width="80%" src="http://www.slicer.org/slicerWiki/images/a/ab/Extensions-Index-to-Catalog-cycle.png"/>

Build instructions
------------------

See http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Developers/Build_ExtensionsIndex

Meta
----

* Code: `git clone git://github.com/Slicer/ExtensionsIndex.git`
* Bugs: http://www.na-mic.org/Bug

License
-------

* [3D Slicer license](http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/License.txt?view=co)


[CDash]: http://slicer.cdash.org/index.php?project=Slicer4
[slicer]: http://slicer.org
[slicer extensions server]: http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Developers/Extensions/Server
[extensions manager]: http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/SlicerApplication/ExtensionsManager
[extension description file]: http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Developers/Extensions/DescriptionFile
[extensions catalog]: http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/Catalog
[extensions server]: http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Developers/Extensions/Server

