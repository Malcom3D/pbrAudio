## License

This project is licensed under the **GNU General Public License v3.0 or later**.

See the [LICENSE](LICENSE) file for the full text.

## pbrAudio
Physically based rendered Audio for Blender.

References [not confirmed]:
- https://graphics.stanford.edu/projects/wavesolver/assets/wavesolver2018_opt.pdf as white paper resources
- https://www.cs.columbia.edu/cg/crumpling/crumpling-sound-synthesis-siggraph-asia-2016-cirio-et-al.pdf for crumpling Sound
- https://www.cs.cornell.edu/projects/Sound/fire/FireSound2011.pdf for fire and explosion sound

- https://github.com/grame-cncm/faust/tree/master-dev/tools/physicalModeling to generate audio physical modal model from 3D mesh
  https://github.com/hrtlacek/faust_python as python cffi binding to faust
- https://github.com/ashab015/Harmonic-Fluids for liquid sound
- https://github.com/SkAT-VG/SDT as physics sound synthesis simulator

- https://github.com/neXyon/audaspace as interface layer from blender and all other pbrAudio systems
- https://github.com/videolabs/libspatialaudio as ambisonic bridge to blender's audaspace
- https://www.acoular.org to generate 3D mappings of sound source from multichannel data recorded by a microphone array (ambisonic)
