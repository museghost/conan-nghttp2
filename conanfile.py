#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


kOPTIONS = ("with_asio", "with_libxml2", "with_jemalloc",
            "with_spdylay", "with_libevent",
            "with_jansson", "with_libcares", "with_libev")

_FIND_PACKAGES = {'with_libxml2': 'find_package(LibXml2 2.6.26)',
                  'with_jemalloc': 'find_package(Jemalloc)',
                  'with_spdylay': 'find_package(Spdylay 1.3.2)',
                  'with_libevent': 'find_package(Libevent 2.0.8 COMPONENTS libevent openssl)',
                  'with_jansson': 'find_package(Jansson  2.5)',
                  'with_libcares': 'find_package(Libcares 1.7.5)',
                  'with_libev': 'find_package(Libev 4.11)'}

class Nghttp2Conan(ConanFile):
    name = "nghttp2"
    version = "1.36.0"
    url = "https://github.com/museghost/nghttp2"
    description = "HTTP/2 C Library and tools"
    license = "https://raw.githubusercontent.com/nghttp2/nghttp2/master/LICENSE"
    settings = "os", "arch", "compiler", "build_type"
    options = {option: [True, False] for option in kOPTIONS}
    default_options = tuple("{0}=False".format(option) for option in options)
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'

    def requirements(self):
        self.requires.add("OpenSSL/1.1.0j@conan/stable")

        if self.options.with_asio:
            self.requires.add("OpenSSL/[>1.0.2a,<1.0.3]@conan/stable")

            for boost_lib in ('Asio', 'System', 'Thread'):
                self.requires.add("Boost.{0}/1.65.1@bincrafters/stable".format(boost_lib))

    def source(self):
        source_url = "https://github.com/museghost/nghttp2.git"
        git = tools.Git(folder="sources")
        git.clone(source_url, "master")
        #tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        #extracted_dir = self.name + "-" + self.version
        #os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_LIB_ONLY"] = True
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder

        #if self.options.shared:
        cmake.definitions['ENABLE_SHARED_LIB'] = True
        cmake.definitions['ENABLE_STATIC_LIB'] = True
        cmake.definitions['BUILD_SHARED_LIBS'] = True
        cmake.definitions['BUILD_STATIC_LIBS'] = True

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

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
         # files are copied by cmake.install()
        pass

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.reverse()
