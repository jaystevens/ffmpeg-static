#!/usr/bin/env python

import os
import sys
import urllib2
import tarfile
import time
import subprocess
import argparse
import multiprocessing

# check python ver 2.6+
if sys.version_info < (2, 6):
    print('need python 2.6+')
    sys.exit(0)
# check python ver < 3
if sys.version_info > (3, 0):
    print('need python 2')
    sys.exit(0)

# TODO - tidy this up/move into class
# check for git
p = subprocess.Popen('which git', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
data = p.communicate()[0]
if data.count('which') > 0:
    print('unable to find git')
    sys.exit(0)

class ffmpeg_build():

    # TODO - check for git
    # TODO - check for library file output, so we can stop build on failure
    # TODO - have libraries build both shared and static?

    def __init__(self, nonfree=False, cflags='', build_static=True):
        self.nonfree = nonfree
        self.cflagsopt = cflags
        self.build_static = build_static

        self.web_server = 'http://www.ghosttoast.com/pub/ffmpeg'

        self.cpuCount = multiprocessing.cpu_count()

        self.app_list()
        self.setup_folder_vars()
        self.setup_env_vars()

    # print env
    #os.system('export 2>/dev/null')

    #cflagsopt = ''
    # native
    #cflagsopt = '-march=native'
    #cflagsopt = '-march=native -fPIC'
    # dcs24 tape2
    #cflagsopt = '-march=core2 -msse4.1'
    #cflagsopt = '-march=core2 -msse4.1 -fPIC'
    # ts
    #cflagsopt = '-march=corei7'
    #clfagsopt = '-march=corei7 -fPIC'

    def app_list(self):
        self.downloadList = []
        self.downloadAuxList = []
        self.gitList = []
        self.fileList = []
        self.downloadListGz = []
        self.fileListGz = []


        self.xz = 'xz-5.2.3'
        self.downloadListGz.append(self.xz)

        self.yasm = 'yasm-1.3.0'
        self.downloadListGz.append(self.yasm)

        self.openssl = 'openssl-1.0.2k'
        self.downloadList.append(self.openssl)

        self.cmake = 'cmake-3.7.2'
        self.downloadList.append(self.cmake)

        self.zlib = 'zlib-1.2.11'
        self.downloadList.append(self.zlib)

        self.bzip2 = 'bzip2-1.0.6'
        self.downloadList.append(self.bzip2)

        self.ncurses = 'ncurses-6.0'
        self.downloadList.append(self.ncurses)

        #self.snappy = 'snappy-1.1.3'
        #self.downloadList.append(self.snappy)

        self.libpng = 'libpng-1.6.28'
        self.downloadList.append(self.libpng)

        self.openjpeg = 'openjpeg-1.5.2'  # ffmpeg works with 1.x, not 2.x
        self.downloadList.append(self.openjpeg)

        self.libtiff = 'tiff-4.0.6'
        self.downloadList.append(self.libtiff)

        self.libogg = 'libogg-1.3.2'
        self.downloadList.append(self.libogg)

        self.libvorbis = 'libvorbis-1.3.5'
        self.downloadList.append(self.libvorbis)

        self.libtheora = 'libtheora-1.1.1'
        self.downloadList.append(self.libtheora)

        self.libvpx = 'libvpx-1.6.1'
        self.downloadList.append(self.libvpx)

        self.speex = 'speex-1.2.0'
        self.downloadList.append(self.speex)

        self.lame = 'lame-3.99.5'
        self.downloadList.append(self.lame)

        self.twolame = 'twolame-0.3.13'
        self.downloadList.append(self.twolame)

        self.soxr = 'soxr-0.1.2'
        self.downloadList.append(self.soxr)

        self.wavpack = 'wavpack-4.80.0'
        self.downloadList.append(self.wavpack)

        self.fdkaac = 'fdk-aac-0.1.5'
        self.downloadList.append(self.fdkaac)

        self.x264 = 'https://git.videolan.org/git/x264.git'
        self.gitList.append(['x264', self.x264])
        self.x264BitDepth = '8'
        self.x264Chroma = 'all'

        self.x265 = 'https://github.com/videolan/x265.git'
        self.gitList.append(['x265', self.x265])

        self.xvid = 'xvid-1.3.4'
        self.downloadList.append(self.xvid)
        self.downloadAuxList.append('xvid_Makefile.patch')

        self.nvenc = 'nvidia_video_sdk_7.1.9'
        self.downloadList.append(self.nvenc)

        self.blackmagic = 'Blackmagic_DeckLink_SDK_10.8.5'
        self.downloadList.append(self.blackmagic)

        self.libgsm = 'libgsm-1.0.13-4'
        self.downloadList.append(self.libgsm)

        #self.libilbc = 'libilbc-20141214-git-ef04ebe'
        self.libilbc = 'libilbc-2.0.2'
        self.downloadList.append(self.libilbc)

        self.webp = 'libwebp-0.6.0'
        self.downloadList.append(self.webp)

        self.opus = 'opus-1.1.4'
        self.downloadList.append(self.opus)

        self.kvazaar = 'kvazaar-1.1.0'
        self.downloadList.append(self.kvazaar)

        self.expat = 'expat-2.2.0'
        self.downloadList.append(self.expat)

        self.freetype = 'freetype-2.7.1'
        self.downloadList.append(self.freetype)

        self.fontconfig = 'fontconfig-2.12.1'
        self.downloadList.append(self.fontconfig)

        self.faac = 'faac-1.28'
        self.downloadList.append(self.faac)

        self.ffmpeg = 'git://source.ffmpeg.org/ffmpeg.git'
        self.gitList.append(['ffmpeg', self.ffmpeg])

        self.ffmbc = 'https://github.com/bcoudurier/FFmbc.git'
        self.gitList.append(['FFmbc', self.ffmbc])

        for item in self.downloadList:
            self.fileList.append('%s.tar.xz' % item)
        for item in self.downloadAuxList:
            self.fileList.append('%s.xz' % item)
        for item in self.downloadListGz:
            itemFn = '%s.tar.gz' % item
            self.fileList.append(itemFn)
            self.fileListGz.append(itemFn)

    def setup_folder_vars(self):
        self.ENV_ROOT = os.getcwd()
        self.TARGET_DIR = os.path.join(self.ENV_ROOT, 'target')
        self.BUILD_DIR = os.path.join(self.ENV_ROOT, 'compile')
        self.BUILD_GIT_DIR = os.path.join(self.ENV_ROOT, 'sourcegit')
        self.TAR_DIR = os.path.join(self.ENV_ROOT, 'sourcetar')

        self.OUT_FOLDER = 'output'
        self.OUT_DIR = os.path.join(self.ENV_ROOT, self.OUT_FOLDER)

    def setup_env_vars(self):
        # setup ENV
        self.ENV_PATH_ORIG = os.getenv('PATH')
        self.ENV_LD_ORIG = os.getenv('LD_LIBRARY_PATH')
        #if sys.platform.startswith('darwin'):  # TODO - fix darwin vars
        #    addpath += ':/opt/local/bin'
        os.putenv('PATH', '%s:%s' % (os.path.join(self.TARGET_DIR, 'bin'), self.ENV_PATH_ORIG))
        os.putenv('LD_LIBRARY_PATH', '%s:%s' % (os.path.join(self.TARGET_DIR, 'lib'), self.ENV_LD_ORIG))
        os.putenv('PKG_CONFIG_PATH', os.path.join(self.TARGET_DIR, 'lib', 'pkgconfig'))
        self.ENV_CFLAGS = '-I%s' % (os.path.join(self.TARGET_DIR, 'include'),)
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS)
        self.ENV_LDFLAGS_STD = ''
        self.ENV_LDFLAGS_STD += '-L%s' % os.path.join(self.TARGET_DIR, 'lib')
        self.ENV_LDFLAGS_STATIC = ' -static -static-libgcc -static-libstdc++'

        self.ENV_LDFLAGS = self.ENV_LDFLAGS_STD
        if self.build_static is True:
            self.ENV_LDFLAGS += self.ENV_LDFLAGS_STATIC

        os.putenv('LDFLAGS', self.ENV_LDFLAGS)
        os.system('export')

    def setupDIR(self):
        for item in [self.ENV_ROOT, self.TARGET_DIR, self.BUILD_DIR, self.BUILD_GIT_DIR, self.TAR_DIR, self.OUT_DIR]:
            os.system('mkdir -p %s' % item)
        old_dir = os.getcwd()
        os.chdir(self.TARGET_DIR)
        os.system('mkdir -p lib')
        os.system('ln -s lib lib64')
        os.chdir(old_dir)

    def cleanTARGET_DIR(self):
        os.system('rm -rf %s' % self.TARGET_DIR)

    def cleanBUILD_DIR(self):
        os.system('rm -rf %s' % self.BUILD_DIR)

    def cleanBUILDGIT_DIR(self):
        os.system('rm -rf %s' % self.BUILD_GIT_DIR)

    def cleanTAR_DIR(self):
        os.system('rm -rf %s' % self.TAR_DIR)

    def cleanOUT_DIR(self):
        os.system('rm -rf %s' % self.OUT_DIR)

    def cleanOUT_DIR_FILES(self):
        os.system('rm -f %s.tar' % self.OUT_DIR)
        os.system('rm -f %s.tar.xz' % self.OUT_DIR)

    def cleanALL(self):
        self.cleanTARGET_DIR()
        self.cleanBUILD_DIR()
        self.cleanTAR_DIR()
        self.cleanOUT_DIR()
        self.cleanOUT_DIR_FILES()

    @staticmethod
    def prewarn():
        print('\nneeded packages:\ngcc git glibc-static (libstdc++-static on some os-es)\n\n')
        x = 2
        while x > 0:
            print(x)
            x = x - 1
            time.sleep(1)

    def f_getfiles(self):
        print('\n*** Downloading files ***\n')
        os.chdir(self.TAR_DIR)
        for fileName in self.fileList:
            fileNamePre, fileNameExt = os.path.splitext(fileName)
            if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.%s' % fileNameExt))) is False:
                try:
                    print('%s/%s' % (self.web_server, fileName))
                    response = urllib2.urlopen('%s/%s' % (self.web_server, fileName))
                    data = response.read()
                except urllib2.HTTPError as e:
                    print('error downloading %s/%s %s' % (self.web_server, fileName, e))
                    sys.exit(1)
                f = open(fileName, 'wb')
                f.write(data)
                f.close()
            else:
                print('%s already downloaded' % fileName.rstrip('.%s' % fileNameExt))
        self.f_sync()

    def f_decompressfiles_gz(self):
        print('\n*** Decompressing gz files ***\n')
        os.chdir(self.BUILD_DIR)
        for fileName in self.fileListGz:
            if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.gz'))) is False:
                os.system('gunzip -v %s' % os.path.join(self.TAR_DIR, fileName))
            else:
                print('%s already uncompressed' % fileName)
        self.f_sync()

    def f_decompressfiles_xz(self):
        print('\n*** Decompressing xz files ***\n')
        os.chdir(self.BUILD_DIR)
        for fileName in self.fileList:
            if fileName.endswith('.xz'):
                if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.xz'))) is False:
                    os.system('%s -dv %s' % (os.path.join(self.TARGET_DIR, 'bin', 'xz'), os.path.join(self.TAR_DIR, fileName)))
                else:
                    print('%s already uncompressed' % fileName)
        self.f_sync()

    def f_repo_clone(self):
        # clone git repos
        for item in self.gitList:
            self.git_clone(item[0], item[1])
        self.f_sync()

    def f_extractfiles(self, gzipMode=False):
        print('\n*** Extracting tar files ***\n')
        os.chdir(self.BUILD_DIR)
        if gzipMode is True:
            fileList = self.fileListGz
        else:
            fileList = self.fileList
        for fileName in fileList:
            fileNamePre, fileNameExt = os.path.splitext(fileName)
            if fileNamePre.lower().endswith('.tar'):
                print(fileNamePre)
                tar = tarfile.open(os.path.join(self.TAR_DIR, fileNamePre))
                tar.extractall()
                tar.close()

    def f_repo_deploy(self):
        for item in self.gitList:
            self.git_deploy(item[0])
        self.f_sync()

    def git_clone(self, name, url):
        print('\n*** Cloning %s ***\n' % name)
        if os.path.exists(os.path.join(self.BUILD_GIT_DIR, name)):
            print('git pull')
            os.chdir(os.path.join(self.BUILD_GIT_DIR, name))
            os.system('git pull')
        else:
            print('git clone')
            os.chdir(self.BUILD_GIT_DIR)
            os.system('git clone %s' % url)

    def git_deploy(self, name):
        print('\n*** Deploy %s git to BUILD_DIR ***\n' % name)
        os.chdir(self.BUILD_GIT_DIR)
        os.system('cp -rf ./%s %s' % (name, self.BUILD_DIR))

    @staticmethod
    def f_sync():
        print('\n*** Syncinig Hard Drive ***\n')
        os.system('sync')

    def b_yasm(self):
        print('\n*** Building yasm ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.yasm))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_xz(self):
        print('\n*** Building xz/liblzma ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.xz))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_curl(self):
        print('\n*** Building curl ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.curl))
        os.putenv('LDFLAGS', self.ENV_LDFLAGS_STD)
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)
        self.f_sync()

    def b_git(self):
        print('\n*** Building git ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.git))
        os.putenv('LDFLAGS', self.ENV_LDFLAGS_STD)
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)
        self.f_sync()

    def b_cmake(self):
        print('\n*** Building cmake ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.cmake))
        os.putenv('LDFLAGS', self.ENV_LDFLAGS_STD)
        os.system('./configure --prefix=%s --parallel=%s' % (self.TARGET_DIR, self.cpuCount))
        os.system('make -j %s && make install' % self.cpuCount)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)

    def b_zlib(self):
        print('\n*** Building zlib ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.zlib))
        cfgcmd = 'export CFLAGS="$CFLAGS -fPIC";./configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --static'
        os.system(cfgcmd)
        os.system('export CFLAGS="$CFLAGS -fPIC";make -j %s && make install' % self.cpuCount)

    def b_bzip2(self):
        print('\n*** Building bzip2 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.bzip2))
        os.system('make CFLAGS="-Wall -Winline -O2 -g -D_FILE_OFFSET_BITS=64 -fPIC"')
        os.system('make install PREFIX=%s' % self.TARGET_DIR)

    def b_ncurses(self):
        print('\n*** Building ncurses ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.ncurses))
        os.system('./configure --with-termlib --with-ticlib --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_openssl(self):
        print('\n*** Building openssl ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.openssl))
        cfgcmd = './Configure --prefix=%s linux-x86_64' % (self.TARGET_DIR)
        if self.build_static is True:
            cfgcmd += ' no-shared'
        else:
            cfgcmd += ' shared'
        os.system(cfgcmd)
        os.system('make depend')
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libpng(self):
        print('\n*** Building libpng ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libpng))
        os.system('./configure --prefix={0}'.format(self.TARGET_DIR))
        os.system('make -j %s && make install' % self.cpuCount)

    def b_openjpeg(self):
        print('\n*** Building openjpeg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.openjpeg))
        os.system('./bootstrap.sh')
        os.system('./configure --disable-png --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libtiff(self):
        print('\n*** Building libtiff ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libtiff))
        if self.build_static is True:
            os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";./configure --prefix=%s --enable-shared=no --enable-static=yes' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.TARGET_DIR))
            os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";make -j %s && make install' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.cpuCount))
        else:
            os.system('export CFLAGS="-I%s";export LDFLAGS="-L%s";./configure --prefix=%s --enable-shared=yes --enable-static=no' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.TARGET_DIR))
            os.system('export CFLAGS="-I%s";export LDFLAGS="-L%s";make -j %s && make install' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.cpuCount))

    def b_libogg(self):
        print('\n*** Building libogg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libogg))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libvorbis(self):
        print('\n*** Building libvorbis ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libvorbis))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libtheora(self):
        print('\n*** Building libtheora ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libtheora))
        cfgcmd = './configure --prefix=%s --disable-examples' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-static --disable-shared'
        else:
            cfgcmd += ' --disable-static'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libvpx(self):
        print('\n*** Building libvpx ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libvpx))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-static --disable-shared'
        else:
            cfgcmd += ' --disable-static --enable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_speex(self):
        print('\n*** Building speex ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.speex))
        os.system('./configure --prefix=%s --enable-sse' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_lame(self):
        print('\n*** Building lame ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.lame))
        cfgcmd = './configure --disable-frontend --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-shared=no --enable-static=yes'
        else:
            cfgcmd += ' --enable-shared=yes --enable-static=no'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_twolame(self):
        print('\n*** Building twolame ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.twolame))
        cfgcmd = './configure --prefix=%s' % (self.TARGET_DIR)
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_soxr(self):
        print('\n*** Building soxr ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.soxr))
        os.system('mkdir Release')
        os.chdir(os.path.join(self.BUILD_DIR, self.soxr, 'Release'))
        if self.build_static is True:
            os.system('cmake -DCMAKE_BUILD_TYPE=Release -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DBUILD_SHARED_LIBS:bool=off ..' % self.TARGET_DIR)
        else:
            os.system('cmake -DCMAKE_BUILD_TYPE=Release -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" ..' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_wavpack(self):
        print('\n*** Building wavpack ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.wavpack))
        cfgcmd = './configure --prefix=%s' % (self.TARGET_DIR)
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_fdkaac(self):
        print('\n*** Building fdk-aac ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.fdkaac))
        cfgcmd = './configure --prefix=%s' % (self.TARGET_DIR)
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_x264(self):
        print('\n*** Building x264 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'x264'))  # for git checkout
        cfgcmd = './configure --prefix=%s --enable-static --disable-cli --disable-opencl --disable-swscale --disable-lavf --disable-ffms --disable-gpac --bit-depth=%s --chroma-format=%s' % (self.TARGET_DIR, self.x264BitDepth, self.x264Chroma)
        if self.build_static is True:
            cfgcmd += ' --enable-static'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_x265(self):
        print('\n*** Build x265 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'x265', 'build', 'linux'))  # for git checkout
        if self.build_static is True:
            os.system('cmake -G "Unix Makefiles" -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DENABLE_SHARED:bool=off ../../source' % self.TARGET_DIR)
        else:
            os.system('cmake -G "Unix Makefiles" -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" ../../source' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_kvazaar(self):
        print('\n*** Build kvazaar ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.kvazaar))
        os.system('./autogen.sh')
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_xvid(self):
        print('\n*** Building xvid ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.xvid, 'build', 'generic'))
        if self.build_static is True:
            # apply patch for static only build
            os.system('cp -f %s ./' % os.path.join(self.TAR_DIR, 'xvid_Makefile.patch'))
            os.system('patch -f < xvid_Makefile.patch')
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        #os.system('rm -f %s' % os.path.join(TARGET_DIR, 'lib', 'libxvidcore.so.*'))

    def b_snappy(self):
        print('\n*** Building snappy ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.snappy))
        # CXX FLAGS
        os.putenv('CXXFLAGS', self.ENV_CFLAGS)  # TODO, check if this is actually useful
        os.system('make clean')
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_blackmagic(self):
        print('\n*** Deploying Blackmagic SDK ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.blackmagic, 'Linux', 'include'))
        os.system('cp -f ./* %s' % os.path.join(self.TARGET_DIR, 'include'))

    def b_nvenc(self):
        print('\n*** Deploying nvenc (Nvidia Video SDK) ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.nvenc, 'Samples', 'common', 'inc'))
        os.system('cp -f ./nvEncodeAPI.h %s' % os.path.join(self.TARGET_DIR, 'include'))

    def b_libgsm(self):
        print('\n*** Building libgsm ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libgsm))
        os.putenv('INSTALL_ROOT', self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        os.unsetenv('INSTALL_ROOT')

    def b_libilbc(self):
        print('\n*** Building libilbc ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libilbc))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_webp(self):
        print('\n*** Building webp ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.webp))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_opus(self):
        print('\n*** Building opus ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.opus))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_expat(self):
        print('\n*** Building expat ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.expat))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' '
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_freetype(self):
        print('\n*** Building freetype ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.freetype))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-shared=no'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_fontconfig(self):
        print('\n*** Building fontconfig ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.fontconfig))
        cfgcmd = './configure --disable-docs --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_faac(self):
        print('\n*** Building faac ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.faac))
        cfgcmd = './configure --without-mp4v2 --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-static --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_ffmpeg(self):
        print('\n*** Building ffmpeg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'ffmpeg'))

        # modify env

        ENV_CFLAGS_NEW = '%s' % self.ENV_CFLAGS
        if self.build_static is True:
            ENV_CFLAGS_NEW += ' --static'
        os.putenv('CFLAGS', ENV_CFLAGS_NEW)
        os.putenv('CPPFLAGS', ENV_CFLAGS_NEW)
        ENV_LDFLAGS_NEW = self.ENV_LDFLAGS
        ENV_LDFLAGS_NEW += ' -fopenmp'  # openmp is needed by soxr
        #ENV_LDFLAGS_NEW += ' -lstdc++'  # stdc++ is needed by snappy
        os.putenv('LDFLAGS', ENV_LDFLAGS_NEW)

        confcmd = ''
        confcmd += './configure --prefix=%s' % self.TARGET_DIR
        confcmd += ' --extra-version=static'
        if self.build_static is True:
            confcmd += ' --pkg-config-flags="--static"'
        confcmd += ' --enable-gpl'
        confcmd += ' --enable-version3'
        if self.nonfree:
            confcmd += ' --enable-nonfree'
        if self.build_static is True:
            confcmd += ' --enable-static'
            confcmd += ' --disable-shared'
        else:
            confcmd += ' --disable-static'
            confcmd += ' --enable-static'
        confcmd += ' --disable-debug'
        confcmd += ' --enable-runtime-cpudetect'
        confcmd += ' --disable-doc'
        confcmd += ' --disable-ffplay'
        confcmd += ' --disable-ffserver'
        confcmd += ' --enable-bzlib'
        confcmd += ' --enable-zlib'
        confcmd += ' --enable-lzma'
        confcmd += ' --enable-libmp3lame'
        confcmd += ' --enable-libopenjpeg'
        confcmd += ' --enable-libopus'
        confcmd += ' --enable-libvorbis'
        confcmd += ' --enable-libtheora'
        confcmd += ' --enable-libvpx'
        confcmd += ' --enable-libspeex'
        confcmd += ' --enable-libx264'
        confcmd += ' --enable-libx265'
        confcmd += ' --enable-libsoxr'
        confcmd += ' --enable-libtwolame'
        confcmd += ' --enable-libwavpack'
        confcmd += ' --enable-libilbc'
        confcmd += ' --enable-libwebp'
        confcmd += ' --enable-libfreetype'
        confcmd += ' --enable-libfontconfig'
        confcmd += ' --enable-libkvazaar'
        # confcmd += ' --enable-librtmp'
        # confcmd += ' --enable-libsnappy'
        # confcmd += ' --enable-libgsm'  # TODO fix headers /inc
        # confcmd += ' --enable-zimg'
        # confcmd += ' --enable-libbluray'
        # confcfg += ' --enable-libschrodeinger'
        # confcmd += ' --disable-devices'
        # confcmd += ' --enable-lto'
        if self.nonfree:
            confcmd += ' --enable-libfdk-aac'
            confcmd += ' --enable-nvenc'
            confcmd += ' --enable-openssl'

        os.system('make distclean')
        os.system(confcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        os.system('make tools/qt-faststart')
        os.system('cp tools/qt-faststart %s' % os.path.join(self.TARGET_DIR, 'bin'))

        # restore env
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)

    def b_ffmbc(self):
        print('\n*** Building ffmbc ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'ffmbc'))

        # modify env

        ENV_CFLAGS_NEW = '%s' % self.ENV_CFLAGS
        if self.build_static is True:
            ENV_CFLAGS_NEW += ' --static'
        os.putenv('CFLAGS', ENV_CFLAGS_NEW)
        os.putenv('CPPFLAGS', ENV_CFLAGS_NEW)
        ENV_LDFLAGS_NEW = self.ENV_LDFLAGS
        ENV_LDFLAGS_NEW += ' -fopenmp'  # openmp is needed by soxr
        # ENV_LDFLAGS_NEW += ' -lstdc++'  # stdc++ is needed by snappy
        os.putenv('LDFLAGS', ENV_LDFLAGS_NEW)

        confcmd = ''
        confcmd += './configure --prefix=%s' % self.TARGET_DIR
        confcmd += ' --extra-version=static'
        #if self.build_static is True:
        #    confcmd += ' --pkg-config-flags="--static"'
        confcmd += ' --enable-gpl'
        if self.nonfree:
            confcmd += ' --enable-nonfree'
        if self.build_static is True:
            confcmd += ' --enable-static'
            confcmd += ' --disable-shared'
        else:
            confcmd += ' --disable-static'
            confcmd += ' --enable-static'
        confcmd += ' --disable-debug'
        confcmd += ' --disable-doc'
        confcmd += ' --enable-bzlib'
        confcmd += ' --enable-zlib'
        confcmd += ' --enable-libmp3lame'
        confcmd += ' --enable-libopenjpeg'
        confcmd += ' --enable-libvorbis'
        confcmd += ' --enable-libtheora'
        confcmd += ' --enable-libvpx'
        confcmd += ' --enable-libspeex'
        confcmd += ' --enable-libx264'
        confcmd += ' --enable-libfaac'
        confcmd += ' --enable-libfreetype'

        os.system('make distclean')
        os.system(confcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        os.system('make tools/qt-faststart')
        os.system('cp tools/qt-faststart %s' % os.path.join(self.TARGET_DIR, 'bin'))

        # restore env
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)

    def out_pack(self):
        os.chdir(self.OUT_DIR)
        for item in ['ffmpeg', 'ffprobe', 'tiffcp', 'tiffinfo', 'qt-faststart']:
            os.system('cp -f {0} ./'.format(os.path.join(self.TARGET_DIR, 'bin', item)))
        if self.build_static is False:
            for item in ['libx265.so.85', 'libvpx.so.4', 'libvorbisenc.so.2', 'libvorbis.so.0', 'libtwolame.so.0', 'libtheoraenc.so.1', 'libtheoradec.so.1', 'libspeex.so.1', 'libopenjpeg.so.1', 'libmp3lame.so.0', 'liblzma.so.5', 'libz.so.1', 'libssl.so.1.0.0', 'libcrypto.so.1.0.0', 'libwebp.so.6', 'libsoxr.so.0', 'libilbc.so.2', 'libfdk-aac.so.1', ]:
                os.system('cp -f {0} ./'.format(os.path.join(self.TARGET_DIR, 'lib', item)))
        os.system('strip *')
        os.chdir(self.ENV_ROOT)
        os.system('tar -cvf ./{0}.tar ./{0}'.format(self.OUT_FOLDER))
        os.system('xz -ve9 ./{0}.tar'.format(self.OUT_FOLDER))

    def u_striplibs(self):
        os.system('strip %s/*' % os.path.join(self.TARGET_DIR, 'bin'))
        os.system('strip %s/*' % os.path.join(self.TARGET_DIR, 'lib'))

    def go_setup(self):
        self.prewarn()
        self.cleanOUT_DIR_FILES()
        self.cleanOUT_DIR()
        self.cleanTARGET_DIR()
        self.cleanBUILD_DIR()

        self.setupDIR()
        self.f_getfiles()
        self.f_decompressfiles_gz()
        self.f_extractfiles(gzipMode=True)
        self.b_yasm()
        self.b_xz()
        self.f_decompressfiles_xz()
        self.f_extractfiles()
        self.f_repo_clone()
        self.f_repo_deploy()

    def go_main(self):
        self.b_openssl()
        self.b_cmake()
        self.b_zlib()
        self.b_bzip2()
        self.b_ncurses()
        #self.b_snappy()
        self.b_libtiff()
        self.b_libpng()
        self.b_openjpeg()
        self.b_libogg()
        self.b_libvorbis()
        self.b_libtheora()
        self.b_libvpx()
        self.b_speex()
        self.b_lame()
        self.b_twolame()
        self.b_soxr()
        self.b_wavpack()
        self.b_x264()
        self.b_x265()
        self.b_xvid()
        self.b_libgsm()
        self.b_libilbc()
        self.b_webp()
        self.b_opus()
        self.b_kvazaar()
        self.b_expat()
        self.b_freetype()
        self.b_fontconfig()
        self.b_blackmagic()
        if self.nonfree:
            self.b_fdkaac()
            self.b_nvenc()
            self.b_openssl()

    def run(self):
        try:
            self.go_setup()
            self.go_main()
            self.b_ffmpeg()
            self.out_pack()
        except KeyboardInterrupt:
            print('\nBye\n')
            sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nonfree', dest='nonfree', help='build non-free/non-redist', action='store_true', default=False)
    parser.add_argument('--cflags', dest='cflags', help='add extra CFLAGS, like -march=native')
    parser.add_argument('-s', '--shared', dest='build_static', help='build shared', action='store_false', default=True)
    parser.add_argument('--setup', dest='do_setup', help='do setup and exit', action='store_true', default=False)
    parser.add_argument('--main', dest='do_main', help='do main and exit', action='store_true', default=False)
    parser.add_argument('--ff', dest='do_ffmpeg', help='do ffmpeg and exit', action='store_true', default=False)
    parser.add_argument('--fb', dest='do_ffmbc', help='do ffmbc and exit', action='store_true', default=False)
    parser.add_argument('--out', dest='do_out', help='do out pack and exit', action='store_true', default=False)
    args = parser.parse_args()

    ffmpegb = ffmpeg_build(nonfree=args.nonfree, cflags=args.cflags, build_static=args.build_static)

    if args.do_setup is True:
        ffmpegb.go_setup()
    elif args.do_main is True:
        ffmpegb.go_main()
    elif args.do_ffmpeg is True:
        ffmpegb.b_ffmpeg()
    elif args.do_ffmbc is True:
        ffmpegb.b_faac()
        ffmpegb.b_ffmbc()
    elif args.do_out is True:
        ffmpegb.out_pack()
    else:
        ffmpegb.run()
