#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

_FIND_PACKAGES = {'with_libxml2': 'find_package(LibXml2 2.6.26)',
                  'with_jemalloc': 'find_package(Jemalloc)',
                  'with_spdylay': 'find_package(Spdylay 1.3.2)',
                  'with_libevent': 'find_package(Libevent 2.0.8 COMPONENTS libevent openssl)',
                  'with_jansson': 'find_package(Jansson  2.5)',
                  'with_libcares': 'find_package(Libcares 1.7.5)',
                  'with_libev': 'find_package(Libev 4.11)'}

class Nghttp2Conan(ConanFile):
    name = "nghttp2"
    version = "1.37.0"
    url = "https://github.com/museghost/nghttp2"
    description = "HTTP/2 C Library and tools"
    license = "https://raw.githubusercontent.com/nghttp2/nghttp2/master/LICENSE"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_asio": [True, False],
               "with_libxml2": [True, False],
               "with_jemalloc": [True, False],
               "with_spdylay": [True, False],
               "with_libevent": [True, False],
               "with_jansson": [True, False],
               "with_libcares": [True, False],
               "with_libev": [True, False]}
    default_options = ("shared=False",
                       "fPIC=True",
                       "with_asio=False",
                       "with_libxml2=False",
                       "with_jemalloc=False",
                       "with_spdylay=False",
                       "with_libevent=False",
                       "with_jansson=False",
                       "with_libcares=False",
                       "with_libev=False")                       
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'

    def requirements(self):
        self.requires.add("OpenSSL/1.0.2r@conan/stable")

        if self.options.with_asio:
            self.requires.add("OpenSSL/[>1.0.2a,<1.0.3]@conan/stable")

            for boost_lib in ('Asio', 'System', 'Thread'):
                self.requires.add("Boost.{0}/1.65.1@bincrafters/stable".format(boost_lib))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        source_url = "https://github.com/museghost/nghttp2.git"
        git = tools.Git(folder="sources")
        git.clone(source_url, "master")
        #tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        #extracted_dir = self.name + "-" + self.version
        #os.rename(extracted_dir, "sources")

    def build(self):
        # git pull
        self.run("cd sources && git pull")

        cmake = CMake(self)
        cmake.definitions["ENABLE_LIB_ONLY"] = True
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder

        if self.options.shared:
            cmake.definitions['ENABLE_SHARED_LIB'] = "ON"
            cmake.definitions['ENABLE_STATIC_LIB'] = "OFF"
            cmake.definitions['BUILD_SHARED_LIBS'] = "ON"
            cmake.definitions['BUILD_STATIC_LIBS'] = "OFF"
        else:
            cmake.definitions['ENABLE_SHARED_LIB'] = "OFF"
            cmake.definitions['ENABLE_STATIC_LIB'] = "ON"
            cmake.definitions['BUILD_SHARED_LIBS'] = "OFF"
            cmake.definitions['BUILD_STATIC_LIBS'] = "ON"

        # Use dependency version of openssl
        openssl_root_dir = self.deps_cpp_info["OpenSSL"].rootpath
        cmake.definitions['OPENSSL_ROOT_DIR'] = openssl_root_dir

        for option in _FIND_PACKAGES:
            if not getattr(self.options, option):
                tools.replace_in_file('sources/CMakeLists.txt', _FIND_PACKAGES[option], '')

        tools.replace_in_file(
            'sources/lib/CMakeLists.txt',
            'DESTINATION "${CMAKE_INSTALL_LIBDIR}"',
            'RUNTIME DESTINATION "bin" LIBRARY DESTINATION "lib" ARCHIVE DESTINATION "lib"')

        tools.replace_in_file(
            'sources/src/CMakeLists.txt',
            'DESTINATION "${CMAKE_INSTALL_LIBDIR}"',
            'RUNTIME DESTINATION "bin" LIBRARY DESTINATION "lib" ARCHIVE DESTINATION "lib"')

        if self.options.with_asio:
            cmake.definitions["ENABLE_ASIO_LIB"] = True

            tools.replace_in_file(
                'sources/CMakeLists.txt',
                'find_package(Boost 1.54.0 REQUIRED system thread)',
                '')

        if self.settings.compiler != 'Visual Studio':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
         # files are copied by cmake.install()
        pass

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.reverse()
