cmake_minimum_required(VERSION 3.30)
project(godot-cpp NONE)

if (WIN32)
	set(OS_SUFFIX "windows")
	set(LIB_SUFFIX ".lib")
elseif (APPLE)
	set(OS_SUFFIX "osx")
	set(LIB_SUFFIX ".a")
elseif (UNIX)
	set(OS_SUFFIX "linux")
	set(LIB_SUFFIX ".a")
else()
	message(FATAL_ERROR "Unsupported platform for godot-cpp")
endif()

if (NOT GODOTCPP_TARGET)
	message(FATAL_ERROR "GODOTCPP_TARGET is not set. (Should be 'debug' or 'release')")
endif()

set(godot-cpp_LIB_NAME "libgodot-cpp.${OS_SUFFIX}.${GODOTCPP_TARGET}.64${LIB_SUFFIX}")
set(godot-cpp_LIB "${CMAKE_INSTALL_PREFIX}/lib/${godot-cpp_LIB_NAME}")

include(CMakePackageConfigHelpers)

configure_package_config_file(
	"${CMAKE_CURRENT_SOURCE_DIR}/godot-cppConfig.cmake.in"
	"${CMAKE_CURRENT_BINARY_DIR}/godot-cppConfig.cmake"
	INSTALL_DESTINATION cmake/godot-cpp
)

write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/godot-cppConfigVersion.cmake"
	VERSION 3.5
	COMPATIBILITY AnyNewerVersion
)

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/bin/${godot-cpp_LIB_NAME}"
		DESTINATION lib
)

install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include/"
		DESTINATION include/godot-cpp
		FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
)

install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/godot-headers/"
		DESTINATION include/godot-cpp/godot-headers
		FILES_MATCHING PATTERN "*.h"
)

install(FILES
	"${CMAKE_CURRENT_BINARY_DIR}/godot-cppConfig.cmake"
	"${CMAKE_CURRENT_BINARY_DIR}/godot-cppConfigVersion.cmake"
	DESTINATION lib/cmake/godot-cpp
)
