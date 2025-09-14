cmake_minimum_required (VERSION 3.5)
project (pbrAudio LANGUAGES C CXX VERSION 0.3.4)
set (CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type: Release or Debug" FORCE)
endif ()

include(ExternalProject)
ExternalProject_Add(
    zarr
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/e0/a3/d3d4fd394a10b1256f9dccb2fe0ddd125fc575d7c437b1c70df050f14176/zarr-3.1.2-py3-none-any.whl
    URL_HASH SHA256=c3e180f53ee0ef91b86f7feff6f9dd381ddd1b512d1a46580530966a493387b6
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    typing-extensions
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/18/67/36e9267722cc04a6b9f15c7f3441c2363321a3ea07da7ae0c0707beb2a9c/typing_extensions-4.15.0-py3-none-any.whl
    URL_HASH SHA256=f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    donfig
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/0c/d5/c5db1ea3394c6e1732fb3286b3bd878b59507a8f77d32a2cebda7d7b7cd4/donfig-0.8.1.post1-py3-none-any.whl
    URL_HASH SHA256=2a3175ce74a06109ff9307d90a230f81215cbac9a751f4d1c6194644b8204f9d
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    yaml
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/75/e4/2c27590dfc9992f73aabbeb9241ae20220bd9452df27483b6e56d3975cc5/PyYAML-6.0.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=3ad2a3decf9aaba3d29c8f537ac4b243e36bef957511b4766cb0057d32b0be85
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    numcodecs
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/01/24/7889b678c0b7e3f605e1ec2fe1ddee0f48920098fecb0cadd5bd66483044/numcodecs-0.16.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=b1b7d8174e14c66191e0e1a4a44dd264bd776fb96b1ce3adc0216154f34b755c
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    packaging
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/20/12/38679034af332785aac8774540895e234f4d07f7545804097de4b666afd8/packaging-25.0-py3-none-any.whl
    URL_HASH SHA256=29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    crc32c
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/6a/2b/9e29e9ac4c4213d60491db09487125db358cd9263490fbadbd55e48fbe03/crc32c-2.7.1-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=d698eec444b18e296a104d0b9bb6c596c38bdcb79d24eba49604636e9d747305
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Get_property(zarr DOWNLOAD_DIR)

# Make a .zip-file which can be installed into Blender
if (NOT WIN32)
  add_custom_target (blender 
    DEPENDS zarr
    DEPENDS typing-extensions
    DEPENDS donfig
    DEPENDS yaml
    DEPENDS crc32c
    DEPENDS packaging
    DEPENDS numcodecs
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
    COMMAND ${CMAKE_COMMAND} -E copy
      "${DOWNLOAD_DIR}/*.whl"
      pbrAudio/wheels
    COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_PROJECT_NAME}.zip" --format=zip pbrAudio
    COMMAND ${CMAKE_COMMAND} -E remove_directory pbrAudio
  )
  add_dependencies(blender zarr)
  add_dependencies(blender yaml)
  add_dependencies(blender crc32c)
  add_dependencies(blender packaging)
  add_dependencies(blender numcodecs)
  add_dependencies(blender donfig)
  add_dependencies(blender typing-extensions)
endif ()
