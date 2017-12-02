#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "nghttp2"
    version = "1.28.0"
    url = "https://github.com/nghttp2/nghttp2"
    description = "HTTP/2 C Library and tools"
    license = "https://raw.githubusercontent.com/nghttp2/nghttp2/master/LICENSE"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'

    def source(self):
        source_url = "https://github.com/nghttp2/nghttp2"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_LIB_ONLY"] = True
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        cmake.definitions["CMAKE_BUILD_SHARED_LIBS"] = self.options.shared

        tools.replace_in_file(
            'sources/lib/CMakeLists.txt',
            'DESTINATION "${CMAKE_INSTALL_LIBDIR}"',
            'RUNTIME DESTINATION "bin" LIBRARY DESTINATION "lib" ARCHIVE DESTINATION "lib"')

        tools.replace_in_file(
            'sources/lib/CMakeLists.txt',
            'add_library(nghttp2 SHARED ${NGHTTP2_SOURCES} ${NGHTTP2_RES})',
            'add_library(nghttp2 ${NGHTTP2_SOURCES} ${NGHTTP2_RES})')

        if not self.options.shared:
            tools.replace_in_file(
                'sources/lib/includes/nghttp2/nghttp2.h',
                '#define NGHTTP2_EXTERN __declspec(dllimport)',
                '#define NGHTTP2_EXTERN')

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
         # files are copied by cmake.install()
        pass

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
