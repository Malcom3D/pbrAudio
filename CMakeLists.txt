cmake_minimum_required (VERSION 3.5)
project (pbrAudio LANGUAGES C CXX VERSION 0.3.4)
set (CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type: Release or Debug" FORCE)
endif ()

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
  if (CMAKE_CXX_FLAGS MATCHES "/W[0-4]")
    string (REGEX REPLACE "/W[0-4]" "/W4" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
  else ()
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")
  endif ()
endif ()

# Helper function for adding source file paths to a list
function (add_paths to)
  set (to_tmp ${${to}})
  foreach (f ${ARGN})
    file (RELATIVE_PATH f_path ${CMAKE_SOURCE_DIR} "${CMAKE_CURRENT_LIST_DIR}/${f}")
    list (APPEND to_tmp "${f_path}")
  endforeach ()
  set (${to} "${to_tmp}" PARENT_SCOPE)
endfunction ()

# Native (backend) shared library
# Collect source files
include (native/CMakeLists.txt)

set (CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

add_library (native SHARED ${NATIVE_SRCS})
set_target_properties (native PROPERTIES PUBLIC_HEADER ${NATIVE_PUBLIC_HEADER})
target_include_directories (native PRIVATE ${NATIVE_HEADERS})

# Dependencies
find_path (SDL2_INCLUDE_DIR SDL2/SDL.h)
find_library (SDL2_LIBRARY SDL2)
find_path (FLUID_INCLUDE_DIR NAMES fluidsynth.h)
find_library (FLUID_LIBRARY fluidsynth)
target_include_directories (native PRIVATE ${SDL2_INCLUDE_DIR})
target_include_directories (native PRIVATE ${FLUID_INCLUDE_DIR})
target_link_libraries (native ${SDL2_LIBRARY})
target_link_libraries (native ${FLUID_LIBRARY})    

# Make a .zip-file which can be installed into Blender
if (NOT WIN32)
  add_custom_target (blender 
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio
    COMMAND ${CMAKE_COMMAND} -E copy
      "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py"
      pbrAudio
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/nodes"
      pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E copy
      $<TARGET_FILE_NAME:native>
      pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_PROJECT_NAME}.zip" --format=zip pbrAudio
    COMMAND ${CMAKE_COMMAND} -E remove_directory pbrAudio
  )
else ()
  add_custom_target (blender 
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio
    COMMAND ${CMAKE_COMMAND} -E copy
      "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py"
      pbrAudio
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/nodes"
      pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/bin
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/Release"
      pbrAudio/bin
    COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_PROJECT_NAME}.zip" --format=zip pbrAudio
    COMMAND ${CMAKE_COMMAND} -E remove_directory pbrAudio
  )
endif ()
add_dependencies (blender native)
