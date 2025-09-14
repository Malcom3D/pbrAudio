cmake_minimum_required (VERSION 3.5)
project (pbrAudio LANGUAGES C CXX VERSION 0.3.4)
set (CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type: Release or Debug" FORCE)
endif ()

# Make a .zip-file which can be installed into Blender
if (NOT WIN32)
  add_custom_target (blender 
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio
    COMMAND ${CMAKE_COMMAND} -E copy
      "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py"
      pbrAudio
    COMMAND ${CMAKE_COMMAND} -E copy
      "${CMAKE_CURRENT_SOURCE_DIR}/blender_manifest.toml"
      pbrAudio
    COMMAND ${CMAKE_COMMAND} -E copy
      "${CMAKE_CURRENT_SOURCE_DIR}/CREDITS"
      pbrAudio
    COMMAND ${CMAKE_COMMAND} -E copy
      "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE"
      pbrAudio
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/engine
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/engine"
      pbrAudio/engine
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/gui
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/gui"
      pbrAudio/gui
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/handlers
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/handlers"
      pbrAudio/handlers
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/nodes"
      pbrAudio/nodes
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/nodetrees
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/nodetrees"
      pbrAudio/nodetrees
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/operators
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/operators"
      pbrAudio/operators
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/sockets
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/sockets"
      pbrAudio/sockets
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/wheels
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/wheels"
      pbrAudio/wheels
    COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_PROJECT_NAME}.zip" --format=zip pbrAudio
    COMMAND ${CMAKE_COMMAND} -E remove_directory pbrAudio
  )
endif ()
