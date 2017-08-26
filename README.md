FFmpeg static build
===================

Three scripts to make a static build of ffmpeg with all the latest codecs and non-free/non-redistributable.

Just follow the instructions below. Once you have the build dependencies,  
just run ./build.py, wait and you should get the ffmpeg binary in target/bin  
to build a non-free/non-redist `./build.py --nonfree`  

Build dependencies (WIP)
------------------

    # Redhat 6x / Centos 6x
    $ yum groupinstall "Development Tools"
    $ yum install git glibc-static libstdc++-static
    $ # EPEL required
    $ rpm -ivh https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
    $ yum install cmake3
    $ ln -s /usr/bin/cmake3 /usr/bin/cmake

    # Fedora 23 / Redhat 7x / Centos 7x
    $ yum groupinstall "Development Tools"
    $ yum install git glibc-static libstdc++-static cmake gperf

    # Debian & Ubuntu
    $ apt-get install build-essential cmake python autoconf

    # OS X - NOT TESTED
    # OS X DOES NOT SHIP STATIC LIBRARIES, this prevents 100% static binaries from being built. so I really do not care about OS X.
    # install XCode, it can be found at http://developer.apple.com/


Codecs
------
* dcadec
* mp3lame
* openjpeg
* vorbis
* theora
* vpx
* speex
* x264
* x265
* soxr
* twolame
* wavpack
* webp
* opus
* iLBC
* blackmagic (Decklink I/O)

Codecs - nonfree
----------------
* openssl
* nvenc (h264/hevc nVidia)
* fdk-aac
* openssl

Codecs TODO
-----------
* schrodeinger
* libmfx (Intel HW accel)
* OpenCORE AMR
* RTMPDump
* VisualOn AMR-WB
* z.lib (zimg)
* GSM - TODO - fix Makefile install /inc
* FreeType
* Fontconfig
* Frei0r
* libass
* libxml2 (dependency)
* libblurray
* libbs2b
* kvazaar (HEVC)
* vid.stab (video stabilization)


Debug
-----

On the top-level of the project, run:

	$ . env.source
	
You can then enter the source folders and make the compilation yourself

	$ cd build/ffmpeg-*
	$ ./configure --prefix=$TARGET_DIR #...
	# ...


TODO
----

 * update `env.source` with the values that match `build.py` 
 * add Python3 support
 * compile `git` to remove OS library dependency
 * compile `cmake` to remove OS library dependency
 * `nasm` support in `mp3lame` (compile ourselves?)
 * test on OS X
 * add support for more codecs and libraries

 
