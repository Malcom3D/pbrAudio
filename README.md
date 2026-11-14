pbrAudio Suite
==============

pbrAudio is a suite for artists and sound designers.
It combines physically based sound synthesis to generate audio from 3D animations and acoustic sound wave propagation through 3D scenes.
The suite is designed to work with any 3D software platform that support python3.11 and includes an addon for blender LTS 4.5.x.


Project Status & Roadmap
=========================

| Component	       | Module            | Version | Current Status	   | Next Milestone |
| :---                 |       :----:      | :----: |      :----:      |           ---: |
| pbrAudioBlender   |                      | 0.2.4 | Beta release   | Sync with pbrAudioRender release  |
| pbrAudioBlender | embreexFromBlender | 4.4.0  | Maintenance | Sync to new embreex version|
| pbrAudioRender   | pbrAudioRay          | 0.1.10 |   Alpha (80%)      | Beta release   |
| pbrAudioRender   | pbrAudioFDTD          | 0.9.1.7 |   Working Alpha (100%)      | Full Rewrite   |
| pbrAudioCommon  |  | 0.2.36 | Alpha (90%)       | Beta release   |
| pbrAudioShaders  | ellipsoidalProxy  | 0.0.11 | Alpha (75%)       | Beta release   |
| pbrAudioShaders  | physicsSolver | 0.2.39 | Beta (90%)       | RC release   |
| pbrAudioShaders  | rigidBody	       | 0.2.36 | Beta (90%)       | RC release   |
| pbrAudioShaders  | fractureSound 	       | 0.2.0 | Beta (40%)       | Beta release   |
| pbrAudioShaders  | particlesSound 	       | 0.1.5 | Alpha (70%)       | Beta release   |
| pbrAudioShaders  | Thin Shell        | 0.0.1 | Alpha (20%)       | Beta release   |
| pbrAudioShaders  | groundSound       | 0.0.1 | Alpha (10%)       | Beta release   |
| pbrAudioShaders  | crumplingSound    |  | WIP               | Alpha release  |
| pbrAudioShaders  | fireSound         |  | WIP               | Alpha release  |
| pbrAudioShaders  | explosionSound    |  | WIP               | Alpha release  |
| pbrAudioShaders  | aeroSound         |  | WIP               | Alpha release  |
| pbrAudioShaders  | fluidSound        |  | WIP               | Alpha release  |
| pbrAudioShaders  | electicSound      |  | WIP               | Alpha release  |
| pbrAudioShaders  | thunderSound      |  | WIP               | Alpha release  |
| pbrAudioShaders  | rainSound         |  | WIP               | Alpha release  |
| pbrAudioShaders  | softBody          |  | WIP               | Alpha release  |
| pbrAudioShaders  | clothSound        |  | WIP               | Alpha release  |
| pbrAudioShaders  | paperSound        |  | WIP               | Alpha release  |
| pbrAudioShaders  | shockWaveSound    |  | WIP               | Alpha release  |
| pbrAudioShaders  | cartoonSound      |  | WIP               | Alpha release  |
| pbrAudioDAW  | pbrAudioDAW | 0.0.2 | Alpha (10%)       | Beta release   | basic TUI are working with playback
| pbrAudioDAW  | pbrAudioDAWgui | 0.0.1 | Alpha (10%)       | Beta release   |
| pbrAudioDAW  | pbrAudioStorage | 0.2.1 | Alpha (95%)       | Beta release   |
| pbrAudioDAW  | pbrAudioSignals | 0.0.18 | Alpha (60%)       | Beta release   |
| pbrAudioDispersion   | objectDisperion          | 0.0.3 |   Alpha (30%)      | Beta release   |


## License

This project is licensed under the **GNU General Public License v3.0 or later**.

See the [LICENSE](LICENSE) file for the full text.


If you use this software in your research, please cite:

```
@software{pbrAudio,
  author = {Malcom3D},
  title = {pbrAudio: Physically Audio Synthesis},
  year = {2025},
  url = {https://github.com/malcom3d/pbrAudio}
}
```

## Support pbrAudio

pbrAudio is a solo, open-source framework that computes **physically-based sound from 3D animation** - rigid bodies, fractures, particles -
and **renders it acoustically** for film, animation, and VFX pipelines.
It is platform-independent and follows the VFX Reference Platform CY2025.
Blender (≥4.5) ships as a reference integration.

Every engine is free and open-source and will stay free.
I'm developing this solo and am currently homeless.
I need ~€500/month for living costs and compute to keep going.

- Monthly support: https://github.com/sponsors/malcom3D
- One-time: https://buymeacoffee.com/malcom3d.gpl
- **Current milestone:** a unified, non-destructive audio-track storage (DAG-based) that lets one scene drive *billions* of tracks
                         (required to listen to the sound of a single raindrop) shipping alongside a working TUI DAW.
- Demo: [https://youtu.be/XeVP_T3gQYY?si=uz1qiA78J1SQ3UsW]

## Supporters & Credits

Thanks to everyone who has supported pbrAudio! See [ACKNOWLEDGMENTS](ACKNOWLEDGMENTS.md) and [CREDITS](CREDITS) for the full list.
