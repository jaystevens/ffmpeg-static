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
git_check_data = p.communicate()[0]
# noinspection PyTypeChecker
if git_check_data.count('which') > 0:
    print('unable to find git')
    sys.exit(0)


# noinspection PyAttributeOutsideInit
class ffmpeg_build:

    # TODO - check for git
    # TODO - check for library file output, so we can stop build on failure
    # TODO - have libraries build both shared and static?

    def __init__(self, nonfree=False, cflags='', build_static=True, init_args=None):
        self.nonfree = nonfree
        self.cflags = cflags
        self.build_static = build_static
        self.args = init_args

        self.web_server = 'http://www.ghosttoast.com/pub/ffmpeg'

        self.cpuCount = multiprocessing.cpu_count()

        # native
        #self.cflags += ' -march=native -mtune=native'
        #self.cflags += ' -march=corei7 -mtune=corei7'
        #self.cflags += ' -march=corei7 -mtune=corei7-avx'
        self.cflags += ' -march=nehalem -mtune=broadwell'
        self.cflags += ' -O3'

        # GCC CFLAGS
        self.ENV_CFLAGS_GCC = '-march=corei7 -mtune=corei7 -O3'

        self.CUDA_SDK = '/usr/local/cuda-9.0'

        self.app_list()
        self.setup_folder_vars()
        self.setup_env_vars()

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

        self.nasm = 'nasm-2.13.03'
        self.downloadList.append(self.nasm)

        self.openssl = 'openssl-1.0.2o'
        self.downloadList.append(self.openssl)

        self.curl = 'curl-7.59.0'
        self.downloadList.append(self.curl)

        self.cmake = 'cmake-3.11.0'
        self.downloadList.append(self.cmake)

        self.zlib = 'zlib-1.2.11'
        self.downloadList.append(self.zlib)

        self.bzip2 = 'bzip2-1.0.6'
        self.downloadList.append(self.bzip2)

        self.ncurses = 'ncurses-6.1'
        self.downloadList.append(self.ncurses)

        self.libpng = 'libpng-1.6.34'
        self.downloadList.append(self.libpng)

        #self.openjpeg = 'openjpeg-1.5.2'  # ffmpeg works with 1.x, not 2.x
        self.openjpeg = 'openjpeg-2.3.0'
        self.downloadList.append(self.openjpeg)

        self.libtiff = 'tiff-4.0.9'
        self.downloadList.append(self.libtiff)

        self.libogg = 'libogg-1.3.3'
        self.downloadList.append(self.libogg)

        self.libvorbis = 'libvorbis-1.3.6'
        self.downloadList.append(self.libvorbis)

        self.libtheora = 'libtheora-1.1.1'
        self.downloadList.append(self.libtheora)

        self.libvpx = 'libvpx-1.7.0'
        self.downloadList.append(self.libvpx)

        self.lame = 'lame-3.100'
        self.downloadList.append(self.lame)

        self.twolame = 'twolame-0.3.13'
        self.downloadList.append(self.twolame)

        self.soxr = 'soxr-0.1.2'
        self.downloadList.append(self.soxr)

        self.fdkaac = 'fdk-aac-0.1.5'
        self.downloadList.append(self.fdkaac)

        self.x264 = 'https://git.videolan.org/git/x264.git'
        self.gitList.append(['x264', self.x264])
        self.x264BitDepth = '8'
        self.x264Chroma = 'all'

        self.x265 = 'https://github.com/videolan/x265.git'
        self.gitList.append(['x265', self.x265])

        self.xvid = 'xvid-1.3.5'
        self.downloadList.append(self.xvid)
        self.downloadAuxList.append('xvid_Makefile.patch')

        #self.nvenc = 'nvidia_video_sdk_8.0.14'
        #self.downloadList.append(self.nvenc)

        self.opus = 'opus-1.2.1'
        self.downloadList.append(self.opus)

        self.expat = 'expat-2.2.5'
        self.downloadList.append(self.expat)

        self.gperf = 'gperf-3.1'
        self.downloadList.append(self.gperf)

        self.glib = 'glib-2.55.0'
        self.downloadList.append(self.glib)

        self.freetype = 'freetype-2.8.1'
        self.downloadList.append(self.freetype)

        self.fontconfig = 'fontconfig-2.12.4'
        self.downloadList.append(self.fontconfig)

        self.fribidi = 'fribidi-0.19.7'
        self.downloadList.append(self.fribidi)

        self.gcc_binutils = 'binutils-2.30'
        self.downloadList.append(self.gcc_binutils)

        self.gcc_glibc = 'glibc-2.27'
        self.downloadList.append(self.gcc_glibc)

        self.gcc_mpfr = 'mpfr-4.0.1'
        self.downloadList.append(self.gcc_mpfr)

        self.gcc_gmp = 'gmp-6.1.2'
        self.downloadList.append(self.gcc_gmp)

        self.gcc_mpc = 'mpc-1.1.0'
        self.downloadList.append(self.gcc_mpc)

        self.gcc_isl = 'isl-0.19'
        self.downloadList.append(self.gcc_isl)

        self.gcc_cloog = 'cloog-0.18.4'
        self.downloadList.append(self.gcc_cloog)

        self.gcc_gcc = 'gcc-7.3.0'
        self.downloadList.append(self.gcc_gcc)

        self.ffmpeg = 'git://source.ffmpeg.org/ffmpeg.git'
        #self.ffmpeg = 'https://bitbucket.org/jaystevens/ffmpeg.git'
        self.gitList.append(['ffmpeg', self.ffmpeg])

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
        self.TARGET_DIR     = os.path.join(self.ENV_ROOT, 'sandbox', 'sys')
        self.TARGET_GCC_DIR = os.path.join(self.ENV_ROOT, 'sandbox', 'sys_gcc')
        self.BUILD_DIR      = os.path.join(self.ENV_ROOT, 'sandbox', 'build')
        self.SRC_GIT_DIR    = os.path.join(self.ENV_ROOT, 'src')
        self.SRC_TAR_DIR    = os.path.join(self.ENV_ROOT, 'src')
        self.OUT_DIR        = os.path.join(self.ENV_ROOT, 'result')

    def setup_env_vars(self):
        # setup ENV
        self.ENV_PATH_ORIG = os.getenv('PATH')
        self.ENV_LD_ORIG = os.getenv('LD_LIBRARY_PATH')
        #if sys.platform.startswith('darwin'):  # TODO - fix darwin vars
        #    addpath += ':/opt/local/bin'

        # PATH
        PATH_FULL = self.ENV_PATH_ORIG
        # add gcc/bin to PATH
        PATH_GCC_BIN = os.path.join(self.TARGET_GCC_DIR, 'bin')
        PATH_FULL = '%s:%s' % (PATH_GCC_BIN, PATH_FULL)
        # add sys/bin to PATH
        PATH_TARGET_BIN = os.path.join(self.TARGET_DIR, 'bin')
        PATH_FULL = '%s:%s' % (PATH_TARGET_BIN, PATH_FULL)
        # add cuda/bin to PATH
        if self.args.cuda is True:
            if os.path.exists(self.CUDA_SDK):
                PATH_FULL = '%s:%s' % (os.path.join(self.CUDA_SDK, 'bin'), PATH_FULL)
        # export PATH
        os.putenv('PATH', PATH_FULL)

        # LD_LIBRARY_PATH
        LD_LIB_FULL = self.ENV_LD_ORIG
        # add gcc/lib to LD_LIB
        PATH_GCC_LIB = os.path.join(self.TARGET_GCC_DIR, 'lib')
        LD_LIB_FULL = '%s:%s' % (PATH_GCC_LIB, LD_LIB_FULL)
        # add gcc/lib64 to LD_LIB
        PATH_GCC_LIB64 = os.path.join(self.TARGET_GCC_DIR, 'lib64')
        LD_LIB_FULL = '%s:%s' % (PATH_GCC_LIB64, LD_LIB_FULL)
        # add sys/lib to LD_LIB
        PATH_TARGET_LIB = os.path.join(self.TARGET_DIR, 'lib')
        LD_LIB_FULL = '%s:%s' % (PATH_TARGET_LIB, LD_LIB_FULL)
        # add cuda/lib to LD_LIB
        if self.args.cuda is True:
            if os.path.exists(self.CUDA_SDK):
                LD_LIB_FULL = '%s:%s' % (os.path.join(self.CUDA_SDK, 'lib64'), LD_LIB_FULL)
        os.putenv('LD_LIBRARY_PATH', LD_LIB_FULL)

        # PKG CONFIG
        os.putenv('PKG_CONFIG_PATH', os.path.join(self.TARGET_DIR, 'lib', 'pkgconfig'))

        # CFLAG
        self.ENV_CFLAGS_STD = ''
        self.ENV_CFLAGS_STD += ' -I%s' % os.path.join(self.TARGET_GCC_DIR, 'include')
        self.ENV_CFLAGS_STD += ' -I%s' % os.path.join(self.TARGET_DIR, 'include')
        if self.args.cuda is True:
            if os.path.exists(self.CUDA_SDK):
                self.ENV_CFLAGS_STD += ' -I%s' % os.path.join(self.CUDA_SDK, 'include')
        self.ENV_CFLAGS_STD += ' %s' % self.cflags
        self.ENV_CFLAGS_STD = self.ENV_CFLAGS_STD.strip()
        self.ENV_CFLAGS = self.ENV_CFLAGS_STD
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS)
        os.putenv('CXXFLAGS', self.ENV_CFLAGS)

        # LDFLAGS
        self.ENV_LDFLAGS_STD = ''
        self.ENV_LDFLAGS_STD += ' -L%s' % os.path.join(self.TARGET_GCC_DIR, 'lib')
        self.ENV_LDFLAGS_STD += ' -L%s' % os.path.join(self.TARGET_GCC_DIR, 'lib64')
        self.ENV_LDFLAGS_STD += ' -L%s' % os.path.join(self.TARGET_DIR, 'lib')
        if self.args.cuda is True:
            if os.path.exists(self.CUDA_SDK):
                self.ENV_LDFLAGS_STD += ' -L%s' % os.path.join(self.CUDA_SDK, 'lib64')
        self.ENV_LDFLAGS_STD = self.ENV_LDFLAGS_STD.strip()
        self.ENV_LDFLAGS = self.ENV_LDFLAGS_STD
        if self.build_static is True:
            self.ENV_LDFLAGS += ' -static -static-libgcc -static-libstdc++'
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)

        # EXPORT
        os.system('hash -r')
        os.system('export')

    def cflags_reset(self):
        print('\nResetting CFLAGS\n')
        print('CFLAGS: {}'.format(self.ENV_CFLAGS))
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS)
        os.putenv('CXXFLAGS', self.ENV_CFLAGS)
        os.system('hash -r')

    def cflags_reset_gcc(self):
        print('\nResetting CFLAGS for gcc build\n')
        print('CFLAGS: {}'.format(self.ENV_CFLAGS))
        os.putenv('CFLAGS', self.ENV_CFLAGS_GCC)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS_GCC)
        os.putenv('CXXFLAGS', self.ENV_CFLAGS_GCC)
        os.system('hash -r')

    def flags_cmake_gcc(self):
        gcc_path = os.path.join(self.TARGET_GCC_DIR, 'bin', 'gcc')
        gxx_path = os.path.join(self.TARGET_GCC_DIR, 'bin', 'g++')
        if os.path.exists(gcc_path):
            print('\nCC: {}\n'.format(gcc_path))
            os.putenv('CC', gcc_path)
            os.putenv('CMAKE_C_COMPILER', gcc_path)
        if os.path.exists(gxx_path):
            print('\nCXX: {}\n'.format(gxx_path))
            os.putenv('CMAKE_CXX_COMPILER', gxx_path)
            os.putenv('CXX', gxx_path)
        os.system('hash -r')

    @staticmethod
    def cflags_clear():
        print('\nClearing CFLAGS\n')
        os.putenv('CFLAGS', '')
        os.putenv('CPPFLAGS', '')
        os.putenv('CXXFLAGS', '')
        os.system('hash -r')

    def setupDIR(self):
        for item in [self.ENV_ROOT, self.TARGET_DIR, self.BUILD_DIR, self.SRC_GIT_DIR, self.SRC_TAR_DIR, self.OUT_DIR, self.TARGET_GCC_DIR]:
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
        os.system('rm -rf %s' % self.SRC_GIT_DIR)

    def cleanTAR_DIR(self):
        os.system('rm -rf %s' % self.SRC_TAR_DIR)

    def cleanOUT_DIR(self):
        os.system('rm -rf %s' % self.OUT_DIR)

    def cleanOUT_DIR_FILES(self):
        os.system('rm -f %s.tar' % self.OUT_DIR)
        os.system('rm -f %s.tar.xz' % self.OUT_DIR)

    def cleanGCC_DIR(self):
        os.system('rm -rf %s' % self.TARGET_GCC_DIR)

    def cleanALL(self):
        self.cleanTARGET_DIR()
        self.cleanBUILD_DIR()
        self.cleanTAR_DIR()
        self.cleanOUT_DIR()
        self.cleanOUT_DIR_FILES()
        #self.cleanGCC_DIR()

    @staticmethod
    def prewarn():
        print('\nneeded packages:\ngcc git glibc-static (libstdc++-static on some os-es)\n\n')
        x = 2
        while x > 0:
            print(x)
            x = x - 1
            time.sleep(1)

    # noinspection PyBroadException
    def f_getfiles(self):
        print('\n*** Downloading files ***\n')
        os.chdir(self.SRC_TAR_DIR)
        for fileName in self.fileList:
            fileNamePre, fileNameExt = os.path.splitext(fileName)
            if os.path.exists(os.path.join(self.SRC_TAR_DIR, fileName.rstrip('.%s' % fileNameExt))) is False:
                try:
                    print('%s/%s' % (self.web_server, fileName))
                    response = urllib2.urlopen('%s/%s' % (self.web_server, fileName))
                    f_data = response.read()
                except urllib2.HTTPError as e:
                    print('error downloading %s/%s %s' % (self.web_server, fileName, e))
                    sys.exit(1)

                try:
                    f = open(fileName, 'wb')
                    f.write(f_data)
                    f.close()
                except:
                    print('error writing downloaded data to file: {}'.format(fileName))
                    sys.exit(1)
            else:
                print('%s already downloaded' % fileName.rstrip('.%s' % fileNameExt))
        self.f_sync()

    def f_decompressfiles_gz(self):
        print('\n*** Decompressing gz files ***\n')
        os.chdir(self.BUILD_DIR)
        for fileName in self.fileListGz:
            if os.path.exists(os.path.join(self.SRC_TAR_DIR, fileName.rstrip('.gz'))) is False:
                os.system('gunzip -v %s' % os.path.join(self.SRC_TAR_DIR, fileName))
            else:
                print('%s already uncompressed' % fileName)
        self.f_sync()

    def f_decompressfiles_xz(self):
        print('\n*** Decompressing xz files ***\n')
        os.chdir(self.BUILD_DIR)
        for fileName in self.fileList:
            if fileName.endswith('.xz'):
                if os.path.exists(os.path.join(self.SRC_TAR_DIR, fileName.rstrip('.xz'))) is False:
                    os.system('%s -dv %s' % (os.path.join(self.TARGET_DIR, 'bin', 'xz'), os.path.join(self.SRC_TAR_DIR, fileName)))
                else:
                    print('%s already uncompressed' % fileName)
        self.f_sync()

    def f_repo_clone(self):
        # clone git repos
        for item in self.gitList:
            self.git_clone(item[0], item[1])
        self.f_sync()

    # noinspection PyPep8Naming
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
                tar = tarfile.open(os.path.join(self.SRC_TAR_DIR, fileNamePre))
                tar.extractall()
                tar.close()

    def f_repo_deploy(self):
        for item in self.gitList:
            self.git_deploy(item[0])
        self.f_sync()

    def git_clone(self, name, url):
        print('\n*** Cloning %s ***\n' % name)
        if os.path.exists(os.path.join(self.SRC_GIT_DIR, name)):
            print('git pull')
            os.chdir(os.path.join(self.SRC_GIT_DIR, name))
            os.system('git pull')
        else:
            print('git clone')
            os.chdir(self.SRC_GIT_DIR)
            os.system('git clone %s' % url)

    def git_deploy(self, name):
        print('\n*** Deploy %s git to BUILD_DIR ***\n' % name)
        os.chdir(self.SRC_GIT_DIR)
        os.system('cp -rf ./%s %s' % (name, self.BUILD_DIR))

    @staticmethod
    def f_sync():
        print('\n*** Syncinig Hard Drive ***\n')
        os.system('sync')

    def check_lib(self, lib_name, lib_display):
        if self.build_static is True:
            lib_ext = 'a'
        else:
            lib_ext = 'so'
        check_lib_path = os.path.join(self.TARGET_DIR, 'lib', '{}.{}'.format(lib_name, lib_ext))
        if not os.path.exists(check_lib_path):
            print('\n{} LIBRARY BUILD FAILED'.format(lib_display))
            print('lib path: {}'.format(check_lib_path))
            sys.exit(1)

    def check_bin(self, bin_name):
        check_bin_path = os.path.join(self.TARGET_DIR, 'bin', bin_name)
        if not os.path.exists(check_bin_path):
            print('\n{} BINARY BUILD FAILED'.format(bin_name))
            print('bin path: {}'.format(check_bin_path))
            sys.exit(1)

    def build_gcc_binutils(self):
        print('\n*** Building gcc binutils ***\n')
        self.cflags_reset_gcc()
        os.chdir(os.path.join(self.BUILD_DIR, self.gcc_binutils))
        os.system('./configure --prefix=%s' % self.TARGET_GCC_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def build_gcc(self):
        print('\n*** Building gcc ***\n')
        self.cflags_reset_gcc()
        os.chdir(os.path.join(self.BUILD_DIR, self.gcc_gcc))
        os.system('ln -sf %s mpfr' % (os.path.join(self.BUILD_DIR, self.gcc_mpfr)))
        os.system('ln -sf %s gmp' % (os.path.join(self.BUILD_DIR, self.gcc_gmp)))
        os.system('ln -sf %s mpc' % (os.path.join(self.BUILD_DIR, self.gcc_mpc)))
        os.system('ln -sf %s isl' % (os.path.join(self.BUILD_DIR, self.gcc_isl)))
        os.system('ln -sf %s cloog' % (os.path.join(self.BUILD_DIR, self.gcc_cloog)))
        os.system('mkdir builddir')
        os.chdir(os.path.join(self.BUILD_DIR, self.gcc_gcc, 'builddir'))
        os.system('../configure --prefix=%s --enable-languages=c,c++,fortran --disable-multilib' % self.TARGET_GCC_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def build_yasm(self, build_new_gcc=False):
        print('\n*** Building yasm ***\n')
        if build_new_gcc is False:
            # this is build before gcc so use "basic" CFLAGS
            self.cflags_reset_gcc()
        else:
            print('\n*** REBUILDING with new GCC ***\n')
            self.cflags_reset()
        os.chdir(os.path.join(self.BUILD_DIR, self.yasm))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libyasm', 'YASM')
        self.check_bin('yasm')

    def build_xz(self, build_new_gcc=False):
        print('\n*** Building xz/liblzma ***\n')
        if build_new_gcc is False:
            # this is build before gcc so use "basic" CFLAGS
            self.cflags_reset_gcc()
        else:
            print('\n*** REBUILDING with new GCC ***\n')
            self.cflags_reset()
        os.chdir(os.path.join(self.BUILD_DIR, self.xz))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('liblzma', 'XZ/LZMA')
        self.check_bin('xz')

    def build_curl(self):
        print('\n*** Building curl ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.curl))
        os.system('./configure --prefix=%s --enable-shared=no --enable-static=yes' % (self.TARGET_DIR))
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_bin('curl')
        self.check_lib('libcurl', 'CURL')

    def build_cmake(self):
        print('\n*** Building cmake ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.cmake))
        os.putenv('LDFLAGS', self.ENV_LDFLAGS_STD)
        os.system('./configure --prefix=%s --parallel=%s' % (self.TARGET_DIR, self.cpuCount))
        os.system('make -j %s && make install' % self.cpuCount)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)
        self.check_bin('cmake')

    def build_zlib(self):
        print('\n*** Building zlib ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.zlib))
        cfgcmd = 'export CFLAGS="$CFLAGS -fPIC";./configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --static'
        os.system(cfgcmd)
        os.system('export CFLAGS="$CFLAGS -fPIC";make -j %s && make install' % self.cpuCount)
        self.check_lib('libz', 'ZLIB')

    def build_bzip2(self):
        print('\n*** Building bzip2 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.bzip2))
        os.system('make CFLAGS="-Wall -Winline -O2 -g -D_FILE_OFFSET_BITS=64 -fPIC"')
        os.system('make install PREFIX=%s' % self.TARGET_DIR)
        self.check_lib('libbz2', 'BZIP2')

    def build_ncurses(self):
        print('\n*** Building ncurses ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.ncurses))
        os.system('./configure --with-termlib --with-ticlib --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libncurses', 'NCURSES')

    def build_nasm(self):
        print('\n*** Building nasm ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.nasm))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_bin('nasm')

    def build_openssl(self):
        print('\n*** Building openssl ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.openssl))
        cfgcmd = './Configure --prefix=%s linux-x86_64' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' no-shared'
        else:
            cfgcmd += ' shared'
        os.system(cfgcmd)
        os.system('make depend')
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libssl', 'OPENSSL')

    def build_libpng(self):
        print('\n*** Building libpng ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libpng))
        os.system('./configure --prefix={0}'.format(self.TARGET_DIR))
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libpng', 'LIBPNG')

    def build_openjpeg(self):
        print('\n*** Building openjpeg ***\n')
        print('OPENJPEG 2.x is still a work in progress')
        return
        os.chdir(os.path.join(self.BUILD_DIR, self.openjpeg))
        # v1
        #os.system('./bootstrap.sh')
        #os.system('./configure --disable-png --prefix=%s' % self.TARGET_DIR)
        #os.system('make -j %s && make install' % self.cpuCount)
        # v2
        os.system('mkdir build')
        os.chdir(os.path.join(self.BUILD_DIR, self.openjpeg, 'build'))
        os.system('cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=0 -DBUILD_CODEC=1 -DCMAKE_INSTALL_PREFIX:PATH=%s' % self.TARGET_DIR)
        os.system('make install')
        self.check_lib('libopenjp2', 'OPENJPEG')

    def build_libtiff(self):
        # TODO 2017-10-27 is this needed to build ffmpeg?
        print('\n*** Building libtiff ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libtiff))
        if self.build_static is True:
            os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";./configure --prefix=%s --enable-shared=no --enable-static=yes' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.TARGET_DIR))
            os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";make -j %s && make install' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.cpuCount))
        else:
            os.system('export CFLAGS="-I%s";export LDFLAGS="-L%s";./configure --prefix=%s --enable-shared=yes --enable-static=no' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.TARGET_DIR))
            os.system('export CFLAGS="-I%s";export LDFLAGS="-L%s";make -j %s && make install' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.cpuCount))
        self.check_lib('libtiff', 'LIBTIFF')

    def build_libogg(self):
        print('\n*** Building libogg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libogg))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libogg', 'LIBOGG')

    def build_libvorbis(self):
        print('\n*** Building libvorbis ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libvorbis))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libvorbis', 'LIBVORBIS')

    def build_libtheora(self):
        print('\n*** Building libtheora ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libtheora))
        cfgcmd = './configure --prefix=%s --disable-examples' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-static --disable-shared'
        else:
            cfgcmd += ' --disable-static'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libtheora', 'LIBTHEORA')

    def build_libvpx(self):
        print('\n*** Building libvpx ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libvpx))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-static --disable-shared'
        else:
            cfgcmd += ' --disable-static --enable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libvpx', 'LIBVPX')

    def build_lame(self):
        print('\n*** Building lame ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.lame))
        cfgcmd = './configure --disable-frontend --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --enable-shared=no --enable-static=yes'
        else:
            cfgcmd += ' --enable-shared=yes --enable-static=no'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libmp3lame', 'LAME/MP3')

    def build_twolame(self):
        print('\n*** Building twolame ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.twolame))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libtwolame', 'TWOLAME/MP2')

    def build_soxr(self):
        print('\n*** Building soxr ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.soxr))
        os.system('mkdir Release')
        os.chdir(os.path.join(self.BUILD_DIR, self.soxr, 'Release'))
        b_cmd = 'cmake'
        b_cmd +=' -DCMAKE_BUILD_TYPE=Release'
        b_cmd +=' -Wno-dev'
        b_cmd +=' -DCMAKE_INSTALL_PREFIX="%s"' % self.TARGET_DIR
        b_cmd +=' -DHAVE_WORDS_BIGENDIAN_EXITCODE=0'
        b_cmd +=' -DWITH_OPENMP=0'  # openMP?
        b_cmd +=' -DBUILD_TESTS=0'
        b_cmd +=' -DBUILD_EXAMPLES=0'
        if self.build_static is True:
            b_cmd +=' -DBUILD_SHARED_LIBS=0'
        b_cmd +=' ..'
        print('b_cmd: {}'.format(b_cmd))
        os.system(b_cmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libsoxr', 'SOXR')

    def build_fdkaac(self):
        print('\n*** Building fdk-aac ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.fdkaac))
        os.system('./autogen.sh')
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        # TODO - 2017-10-27 add lib check

    def build_x264(self):
        print('\n*** Building x264 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'x264'))  # for git checkout
        cfgcmd = './configure --prefix=%s --enable-static --disable-cli --disable-opencl --disable-swscale --disable-lavf --disable-ffms --disable-gpac --bit-depth=%s --chroma-format=%s' % (self.TARGET_DIR, self.x264BitDepth, self.x264Chroma)
        if self.build_static is True:
            cfgcmd += ' --enable-static'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libx264', 'X264')

    def build_x265(self):
        print('\n*** Build x265 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'x265', 'build', 'linux'))  # for git checkout
        if self.build_static is True:
            os.system('cmake -G "Unix Makefiles" -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DENABLE_SHARED:bool=off ../../source' % self.TARGET_DIR)
        else:
            os.system('cmake -G "Unix Makefiles" -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" ../../source' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libx265', 'X265')

    def build_xvid(self):
        print('\n*** Building xvid ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.xvid, 'build', 'generic'))
        if self.build_static is True:
            # apply patch for static only build
            os.system('cp -f %s ./' % os.path.join(self.SRC_TAR_DIR, 'xvid_Makefile.patch'))
            os.system('patch -f < xvid_Makefile.patch')
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        #os.system('rm -f %s' % os.path.join(TARGET_DIR, 'lib', 'libxvidcore.so.*'))
        self.check_lib('libxvidcore', 'XVID')

    #def build_nvenc(self):
    #    # TODO - 2017-10-27 is this still needed to build ffmpeg?
    #    print('\n*** Deploying nvenc (Nvidia Video SDK) ***\n')
    #    os.chdir(os.path.join(self.BUILD_DIR, self.nvenc, 'Samples', 'common', 'inc'))
    #    os.system('cp -f ./nvEncodeAPI.h %s' % os.path.join(self.TARGET_DIR, 'include'))

    def build_opus(self):
        print('\n*** Building opus ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.opus))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libopus', 'OPUS')

    def build_expat(self):
        print('\n*** Building expat ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.expat))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' '
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libexpat', 'EXPAT')

    def build_gperf(self):
        print('\n*** Building gperf ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.gperf))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' '
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        # TODO - 2017-10-27 add check output [check_lib/check_bin]

    def build_glib(self):
        print('\n*** Building glib ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.glib))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        cfgcmd += ' --enable-libmount=no'
        cfgcmd += ' --with-pcre=internal'
        if self.build_static is True:
            cfgcmd += ' --enable-shared=no'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libglib-2.0', 'GLIB')

    def build_freetype(self):
        print('\n*** Building freetype ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.freetype))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        # harfbuzz is a bitch to compile
        cfgcmd += ' --with-harfbuzz=no'
        if self.build_static is True:
            cfgcmd += ' --enable-shared=no'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libfreetype', 'FREETYPE')

    def build_fontconfig(self):
        print('\n*** Building fontconfig ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.fontconfig))
        cfgcmd = './configure --disable-docs --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libfontconfig', 'FONTCONFIG')

    def build_fribidi(self):
        print('\n*** Building fribidi ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.fribidi))
        cfgcmd = './configure --prefix=%s' % self.TARGET_DIR
        if self.build_static is True:
            cfgcmd += ' --disable-shared'
        os.system(cfgcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        self.check_lib('libfribidi', 'FRIBIDI')

    def build_cuda(self):
        print('\n*** Setup cuda ***\n')

        # libcuda.so fix
        CUDA_SO  = '/usr/lib64/nvidia/libcuda.so'
        CUDA_SO1 = '/usr/lib64/nvidia/libcuda.so.1'
        if os.path.exists(CUDA_SO):
            os.system('ln -s {} {}'.format(CUDA_SO, os.path.join(self.TARGET_DIR, 'lib')))
        if os.path.exists(CUDA_SO1):
            os.system('ln -s {} {}'.format(CUDA_SO1, os.path.join(self.TARGET_DIR, 'lib64')))


    def build_ffmpeg(self):
        print('\n*** Building ffmpeg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'ffmpeg'))

        self.cflags_reset()
        self.flags_cmake_gcc()

        # modify env
        ENV_CFLAGS_FF = self.ENV_CFLAGS
        if self.build_static is True:
            ENV_CFLAGS_FF += ' --static'
        if self.args.taco is True:
            ENV_CFLAGS_FF = ENV_CFLAGS_FF.replace(' --static ', ' ')  # disable static for taco build
        os.putenv('CFLAGS', ENV_CFLAGS_FF)
        os.putenv('CPPFLAGS', ENV_CFLAGS_FF)
        os.putenv('CXXFLAGS', ENV_CFLAGS_FF)
        ENV_LDFLAGS_FF = self.ENV_LDFLAGS
        ENV_LDFLAGS_FF += ' -fopenmp -lm'  # openmp is needed by soxr [this should be removeable 2017-10-25]
        # CUDA can not be LD static, it needs runtime linking :(
        if (self.args.cuda is True) or (self.args.taco is True):
            ENV_LDFLAGS_FF = ENV_LDFLAGS_FF.replace(' -static ', ' ')

        os.putenv('LDFLAGS', ENV_LDFLAGS_FF)

        os.putenv('LDLIBFLAGS', '-fopenmp -lm')
        os.system('hash -r')

        os.system('export')

        confcmd = './configure'
        confcmd += ' --prefix=%s' % self.TARGET_DIR
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
        #confcmd += ' --disable-debug'               # disable debugging
        confcmd += ' --enable-runtime-cpudetect'    # should be on all the time
        confcmd += ' --disable-doc'                 # disable building doc
        confcmd += ' --disable-ffplay'              # do not compile ffplay
        confcmd += ' --disable-ffserver'            # do not compile ffserver
        confcmd += ' --enable-bzlib'                # bz2
        confcmd += ' --enable-zlib'                 # zlib
        confcmd += ' --enable-lzma'                 # lzma (xz)
        #confcmd += ' --enable-libmp3lame'          # AUDIO - mp3
        #confcmd += ' --enable-libopenjpeg'         # VIDEO - jpeg2000          # v2 WIP
        confcmd += ' --enable-libopus'              # AUDIO - opus
        #confcmd += ' --enable-libvorbis'           #       - vorbis
        #confcmd += ' --enable-libtheora'           #       - theora
        confcmd += ' --enable-libvpx'               # VIDEO - VP8/VP9
        confcmd += ' --enable-libx264'              # VIDEO - H264
        confcmd += ' --enable-libx265'              # VIDEO - H265/HEVC
        confcmd += ' --enable-libsoxr'              # AUDIO - RESMAPLE
        confcmd += ' --enable-libtwolame'           # AUDIO - MP2
        confcmd += ' --enable-libfreetype'          # VF    - fonts/drawtext
        confcmd += ' --enable-libfontconfig'        # VF    - fonts/drawtext
        confcmd += ' --enable-libfribidi'           # VF    - fonts/drawtext
        # confcmd += ' --enable-zimg'               # VF    - resize zscale
        # confcmd += ' --enable-libbluray'          # FORMAT- reading bluray
        # confcmd += ' --disable-devices'           # 
        confcmd += ' --enable-hardcoded-tables'     # Hardcoded tables - speeds up start a little
        confcmd += ' --enable-avresample'           # FILTER- RESAMPLE
        confcmd += ' --disable-cuvid'               # nVidia Cuvid Decoder - Broken/bad - nonfree
        #confcmd += ' --enable-nvenc'               # nVidia NVENC h264/h265 encoder
        confcmd += ' --disable-nvenc'               # nVidia NVENC - seg faults on linux
        #confcmd += ' --enable-opencl'              # OpenCL is used for some filters [no-encode/decode support]
        if self.args.taco is True:
            confcmd += ' --enable-mainconcept'
            confcmd += ' --extra-ldflags="-L/myproj/mainconcept/lib"'
            confcmd += ' --extra-cflags="-I/myproj/FFmpeg/mainconcept/include"'

        #confcmd += ' --extra-cflags="{}"'.format(ENV_CFLAGS_NEW)
        confcmd += ' --extra-ldlibflags="-lm"'      # this fixes 3rd party libs
        confcmd += ' --extra-libs="-lm"'            # this fixes 3rd party libs
        if self.nonfree:
            confcmd += ' --enable-libfdk-aac'       # AUDIO - AAC FDK Library
            confcmd += ' --enable-openssl'          # FORMAT- openssl/util
            if self.args.cuda is True:
                if os.path.exists(self.CUDA_SDK):
                    print('FOUND CUDA SDK: {}'.format(self.CUDA_SDK))
                    #confcmd += ' --extra-ldlibflags="-lcudart"'   # require cudart [runtime]
                    confcmd += ' --enable-cuda-sdk'             # nVidia CUDA processing
                    confcmd += ' --enable-libnpp'           # nVidia CUDA NPP
                    confcmd += ' --nvccflags="-gencode arch=compute_61,code=sm_61 -O2"'



        os.system('make distclean')
        os.system(confcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        os.system('make tools/qt-faststart')
        os.system('cp tools/qt-faststart %s' % os.path.join(self.TARGET_DIR, 'bin'))

        # restore env
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('CPPFLAGS', self.ENV_CFLAGS)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)

        self.check_bin('ffmpeg')

    def util_out_pack(self):
        os.chdir(self.OUT_DIR)
        for item in ['ffmpeg', 'ffprobe', 'tiffcp', 'tiffinfo', 'qt-faststart']:
            os.system('cp -f {0} ./'.format(os.path.join(self.TARGET_DIR, 'bin', item)))
        if self.build_static is False:
            for item in ['libx265.so.85', 'libvpx.so.4', 'libvorbisenc.so.2', 'libvorbis.so.0', 'libtwolame.so.0', 'libtheoraenc.so.1', 'libtheoradec.so.1', 'libspeex.so.1', 'libopenjpeg.so.1', 'libmp3lame.so.0', 'liblzma.so.5', 'libz.so.1', 'libssl.so.1.0.0', 'libcrypto.so.1.0.0', 'libwebp.so.6', 'libsoxr.so.0', 'libilbc.so.2', 'libfdk-aac.so.1', ]:
                os.system('cp -f {0} ./'.format(os.path.join(self.TARGET_DIR, 'lib', item)))
        os.system('strip *')
        os.system('tar -cvf ../result.tar ./')
        os.chdir(self.ENV_ROOT)
        os.system('xz -ve9 ./result.tar')

    def util_striplibs(self):
        # not used, for shared
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
        self.build_yasm()
        self.build_xz()
        self.f_decompressfiles_xz()
        self.f_extractfiles()
        self.f_repo_clone()
        self.f_repo_deploy()

    def go_gcc(self):
        GCC_DO_BUILD = True
        if os.path.exists(os.path.join(self.TARGET_GCC_DIR, 'bin', 'gcc')):
            GCC_DO_BUILD = False

        if self.args is not None:
            if self.args.do_gcc is True:
                GCC_DO_BUILD = True

        if GCC_DO_BUILD is True:
            self.build_gcc_binutils()
            self.build_gcc()

    def go_main(self):
        self.cflags_reset()
        self.flags_cmake_gcc()
        self.build_zlib()
        self.build_yasm(build_new_gcc=True)
        self.build_xz(build_new_gcc=True)
        self.build_nasm()
        self.build_openssl()
        self.build_curl()
        self.build_cmake()
        self.build_bzip2()
        self.build_ncurses()
        self.build_libtiff()
        self.build_libpng()
        self.build_openjpeg()
        self.build_libogg()
        self.build_libvorbis()
        self.build_libtheora()
        self.build_libvpx()
        self.build_lame()
        self.build_twolame()
        self.build_soxr()
        self.build_x264()
        self.build_x265()
        self.build_xvid()
        self.build_opus()
        self.build_expat()
        self.build_gperf()
        self.build_glib()
        self.build_freetype()
        self.build_fontconfig()
        self.build_fribidi()
        self.build_cuda()
        if self.nonfree:
            self.go_main_nonfree()

    def go_main_nonfree(self):
        self.cflags_reset()
        self.flags_cmake_gcc()
        self.build_fdkaac()
        #self.build_nvenc()

    def run(self):
        try:
            self.go_setup()
            if self.args is not None:
                if self.args.do_skipgcc is False:
                    self.go_gcc()
            self.go_main()
            self.build_ffmpeg()
            self.util_out_pack()
        except KeyboardInterrupt:
            print('\nBye\n')
            sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nonfree', dest='nonfree', help='build non-free/non-redist', action='store_true', default=True)
    parser.add_argument('--cflags', dest='cflags', help='add extra CFLAGS, like -march=native', default='')
    parser.add_argument('--cuda', dest='cuda', help='build with cuda dynamic linking', action='store_true', default=False)
    parser.add_argument('-s', '--shared', dest='build_static', help='build shared', action='store_false', default=True)
    parser.add_argument('--setup', dest='do_setup', help='do setup ONLY and exit', action='store_true', default=False)
    parser.add_argument('-m', '--main', dest='do_main', help='do main ONLY and exit', action='store_true', default=False)
    parser.add_argument('-mf', '--main_nonfree', dest='do_main_nf', help='do main nonfree ONLY and exit', action='store_true', default=False)
    parser.add_argument('-f', '--ff', dest='do_ffmpeg', help='do ffmpeg ONLY and exit', action='store_true', default=False)
    parser.add_argument('--out', dest='do_out', help='do out pack and exit', action='store_true', default=False)
    parser.add_argument('--gcc', dest='do_gcc', help='do gcc build ONLY and exit', action='store_true', default=False)
    parser.add_argument('--test', dest='do_test', help='do test and exit', action='store_true', default=False)
    parser.add_argument('--skipgcc', dest='do_skipgcc', help='skip building gcc', action='store_true', default=False)
    parser.add_argument('--taco', dest='taco', help='taco mode', action='store_true', default=False)
    args = parser.parse_args()

    ffx = ffmpeg_build(nonfree=args.nonfree, cflags=args.cflags, build_static=args.build_static, init_args=args)

    if args.do_setup is True:
        ffx.go_setup()
    elif args.do_main is True:
        ffx.go_main()
    elif args.do_main_nf is True:
        ffx.go_main_nonfree()
    elif args.do_ffmpeg is True:
        ffx.build_ffmpeg()
    elif args.do_out is True:
        ffx.util_out_pack()
    elif args.do_gcc is True:
        ffx.go_gcc()
    elif args.do_test is True:
        os.system('gcc --version')
        ffx.build_cuda()
        #ffx.build_glib()
    else:
        ffx.run()
