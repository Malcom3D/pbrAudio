- in the Render tab:
  - properties to set the device (cpu, gpu)
  - properties to configure graphical preview render engine to visualize result (EEVE, Cycle).
  - properties to configure audio preview and render in the Audio Sampling panel
  - properties to configure and start(with button) audio prebake in the Audio PreBake panel for physically based synthesis nodes (modal physical model, harmonic fluids)
  - properties to configure and start(with button) audio bake in the Audio Bake panel
  - properties to configure the cache directory path Cache panel
  - properties to configure audio denoise with gate and limiter in the Audio Denoise panel
  - properties to configure performance in the Audio Performance panel
  - display and inherit blender's Grease Pencil panel
- in the Output tab:
  - properties to configure type(https://github.com/ebu/ebu_adm_renderer), channels number, sample format, sample rate in the Format panel
  - output directory, output file format in the Output panel
  - diplay and inherit blender's frame rate and frame range properties in the Video Sync panel
  - metada properties in the Metadata panel
- in the World tab:
  - properties to select an AudioWorld node tree or an ambisonic file in the Environment panel
  - if an ambisonic file is selected display metadata and info in the Info panel
  - if an ambisonic file is selected, parameters to configure the dimension and parameters of the 3D sound sphere
- in the Material tab:
  - material can be added to object or vertex group
  - properties to select a simple AudioMaterial and an AudioMaterial node tree in the AudioMaterial panel
  - display customizable parameters of the simple AudioMaterial preset
  - if an AudioMaterial node tree is selected display it's name

- a dedicated node tree system "pbrAudio Node Editor" with "AudioMaterial" and "AudioWorld" node tree types
  - in the pbrAudio Node Editor a drop-down menu to change from object(to display AudioMaterial node tree) and world(to display AudioWorld node tree) types, like this https://artisticrender.com/wp-content/uploads/2023/01/blender_world_shader_type.png

- for the AudioMaterial node tree:
  - one input node with sound file selection and audio output socket
  - one output node with audio, position and orientation input socket
  - one geometric node with object selection and shape, position, orientation output socket
  - one collisions detection node with one collisions output socket
  - one "Modal Physical Model Generator" node with parameter for the Generator(https://github.com/grame-cncm/faust/tree/master-dev/tools/physicalModeling/mesh2faust), with shape and collisions input socket and audio output socket
  - one "Harmonic Fluids" node with fluid simulation selection and one audio output socket

- The "Modal Physical Model Generator" node must:
  - export the object shape as obj file in the cache directory
  - run mush2faust with parameters, limiting the exitation points to the vertices ID from collisions detection node and save the results in the cache directory
  - write Faust functions implementing the physical models generated in the cache directory

- The "Harmonic Fluids" node must:
  - extract the coordinates and sizes of bubbles in the selected fluid simulation
  - extract shape information of fluid surface from the selected fluid simulation
  - prepare the simulation as described in https://www.cs.cornell.edu/projects/HarmonicFluids/harmonicfluids.pdf using https://github.com/ashab015/Harmonic-Fluids

- for the WorldMaterial node tree:
  - one input node with ambisonics sound file selection and position data, with position/ambisonic output socket
  - one geometric node with domain object selection and shape, position, orientation output socket
  - one volumetric 3d sound mapping decoder node with dynamic multiple position/ambisonic input and one 3d sound sources output socket
  - one auralization node with:
    - acoustic parameters
    - one domain shape input socket
    - one domain position input socket
    - one domain orientation input socket
    - one environment position/ambisonic input socket
    - one 3d sound sources position/ambisonic input socket
    - one complex audio output socket
  - one world output node with one complex audio input socket

The auralization node must:
- export all 3d object in the domain as a obj file in the cache directory
- export all 3d object position/orientation in the domain  as numpy npz file in the cache directory
- export all 3d audio sources position/orientation in the domain  as numpy npz file in the cache directory
- for any 3d audio sources in the domain export all audio sound as numpy.ndarray, in a numpy npz file in the cache directory
- write a python script for a multiple/nested domains time domain simulation for https://github.com/optimuslib/optimus using the exported data in the cache directory and save results as point cloud using a "per sample rate as frame rate" openvdb file format in the cache directory

The audio preview must start and stop in sync with blender's animation playback.
Audio render must begin with ctrl-F12
