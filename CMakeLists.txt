cmake_minimum_required (VERSION 3.5)
project (pbrAudio LANGUAGES C CXX VERSION 0.3.4)
set (CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type: Release or Debug" FORCE)
endif ()

include(ExternalProject)
ExternalProject_Add(
    scipy
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/1a/bc/a5c75095089b96ea72c1bd37a4497c24b581ec73db4ef58ebee142ad2d14/scipy-1.16.2-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=f5db5ba6188d698ba7abab982ad6973265b74bb40a1efe1821b58c87f73892b9
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pywavelets
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/d8/8c/f316a153f7f89d2753df8a7371d15d0faab87e709fe02715dbc297c79385/pywavelets-1.9.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=d76b7fa8fc500b09201d689b4f15bf5887e30ffbe2e1f338eb8470590eb4521a
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    locket
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/db/bc/83e112abc66cd466c6b83f99118035867cecd41802f8d044638aa78a106e/locket-1.0.0-py2.py3-none-any.whl
    URL_HASH SHA256=b6c819a722f7b6bd955b80781788e4a66a55628b858d347536b7e81325a3a5e3
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    partd
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/71/e7/40fb618334dcdf7c5a316c0e7343c5cd82d3d866edc100d98e29bc945ecd/partd-1.4.2-py3-none-any.whl
    URL_HASH SHA256=978e4ac767ec4ba5b86c6eaa52e5a2a3bc748a2ca839e8cc798f1cc6ce6efb0f
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    zipp
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/2e/54/647ade08bf0db230bfea292f893923872fd20be6ac6f53b2b936ba839d75/zipp-3.23.0-py3-none-any.whl
    URL_HASH SHA256=071652d6115ed432f5ce1d34c336c0adfd6a884660d1e9712a256d3d3bd4b14e
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    importlib_metadata
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/20/b0/36bd937216ec521246249be3bf9855081de4c5e06a0c9b4219dbeda50373/importlib_metadata-8.7.0-py3-none-any.whl
    URL_HASH SHA256=e5dd1551894c77868a30651cef00984d50e1002d06942a7101d34870c5f02afd
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    toolz
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/03/98/eb27cc78ad3af8e302c9d8ff4977f5026676e130d28dd7578132a457170c/toolz-1.0.0-py3-none-any.whl
    URL_HASH SHA256=292c8f1c4e7516bf9086f8850935c799a874039c8bcf959d47b600e4c44a6236
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    fsspec
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/47/71/70db47e4f6ce3e5c37a607355f80da8860a33226be640226ac52cb05ef2e/fsspec-2025.9.0-py3-none-any.whl
    URL_HASH SHA256=530dc2a2af60a414a832059574df4a6e10cce927f6f4a78209390fe38955cfb7
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    cloudpickle
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/7e/e8/64c37fadfc2816a7701fa8a6ed8d87327c7d54eacfbfb6edab14a2f2be75/cloudpickle-3.1.1-py3-none-any.whl
    URL_HASH SHA256=c8c5a44295039331ee9dad40ba100a9c7297b6f988e50e87ccdf3765a668350e
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    click
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/db/d3/9dcc0f5797f070ec8edf30fbadfb200e71d9db6b84d211e3b2085a7589a0/click-8.3.0-py3-none-any.whl
    URL_HASH SHA256=9b9f285302c6e3064f4330c05f05b81945b2a39544279343e6e7c5f27a9baddc
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    dask
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/25/60/3fcd548bed6d25016933e4b2984c9b82e4c1e760380e03d4100b1b4726e0/dask-2025.9.1-py3-none-any.whl
    URL_HASH SHA256=2a8a7dc933caaea2f47745a65a6ec93d9e616e12aab53b4f03ee161d31939110
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    numba
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/0e/7d/403be3fecae33088027bc8a95dc80a2fda1e3beff3e0e5fc4374ada3afbe/numba-0.62.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=604059730c637c7885386521bb1b0ddcbc91fd56131a6dcc54163d6f1804c872
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    llvmlite
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/e6/95/a13362fe71d1e88bea9e3cc58a3337b3302a3e4af68391df10389f3b7f78/llvmlite-0.45.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=c6815d0d3f96de34491d3dc192e11e933e3448ceff0b58572a53f39795996e01
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    soundfile
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/57/5e/70bdd9579b35003a489fc850b5047beeda26328053ebadc1fb60f320f7db/soundfile-0.13.1-py2.py3-none-manylinux_2_28_x86_64.whl
    URL_HASH SHA256=03267c4e493315294834a0870f31dbb3b28a95561b80b134f0bd3cf2d5f0e618
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    cffi
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/d7/91/500d892b2bf36529a75b77958edfcd5ad8e2ce4064ce2ecfeab2125d72d1/cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=8941aaadaf67246224cee8c3803777eed332a19d909b47e29c9842ef1e79ac26
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    rich
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/e3/30/3c4d035596d3cf444529e0b2953ad0466f6049528a879d27534700580395/rich-14.1.0-py3-none-any.whl
    URL_HASH SHA256=536f5f1785986d6dbdea3c75205c473f970777b4a0d6c6dd1b696aa05a3fa04f
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    zarrs
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/f4/45/95f2b85b80d586c9a1227def9fbc0b0c3181a45445d5599288554c562a72/zarrs-0.2.0-cp311-abi3-manylinux_2_28_x86_64.whl
    URL_HASH SHA256=2551112c2159e349d19c3e27f6a213f74ab0d016b4862c9474bdbe690f1f46ae
    BUILD_ALWAYS OFF
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
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
    DEPENDS scipy
    DEPENDS pywavelets
    DEPENDS locket
    DEPENDS partd
    DEPENDS zipp
    DEPENDS importlib_metadata
    DEPENDS toolz
    DEPENDS fsspec
    DEPENDS cloudpickle
    DEPENDS click
    DEPENDS dask
    DEPENDS numba
    DEPENDS llvmlite
    DEPENDS soundfile
    DEPENDS cffi
    DEPENDS rich
    DEPENDS zarrs
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
    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/properties
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      "${CMAKE_CURRENT_SOURCE_DIR}/properties"
      pbrAudio/properties
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
  add_dependencies(blender scipy)
  add_dependencies(blender pywavelets)
  add_dependencies(blender locket)
  add_dependencies(blender partd)
  add_dependencies(blender zipp)
  add_dependencies(blender importlib_metadata)
  add_dependencies(blender toolz)
  add_dependencies(blender fsspec)
  add_dependencies(blender cloudpickle)
  add_dependencies(blender click)
  add_dependencies(blender dask)
  add_dependencies(blender numba)
  add_dependencies(blender llvmlite)
  add_dependencies(blender soundfile)
  add_dependencies(blender cffi)
  add_dependencies(blender rich)
  add_dependencies(blender zarrs)
  add_dependencies(blender zarr)
  add_dependencies(blender yaml)
  add_dependencies(blender crc32c)
  add_dependencies(blender packaging)
  add_dependencies(blender numcodecs)
  add_dependencies(blender donfig)
  add_dependencies(blender typing-extensions)
endif ()
