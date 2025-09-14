/__init__.py                      
                # registra il nodetree vuoto da nodetree/
                # registra i sockets da sockets/
                # registra i moduli (audionodes, audaspace, libspatialaudio, SDT, ...) dalle rispettive directory

nodetree/
         __init__.py
         pbrAudioNT.py              # funzioni init(), update(), ecc di base (che puntano a quelle dei moduli?)

/sockets/
         __init__.py                # registra le classi Socket definite nei files locali
                                    # from . import *
                                    # packageName = '[packageName]'
                                    # socketNames = []
                                    # for file in glob.glob(packageName + '*.py'):
                                    #     if not '__init__' in file:
                                    #        socketNames.append(files.replace(packageName, '').replace('/', '').replace('.py', ''))
                                    # def register():
                                    # for socket in socketNames:
                                    #     register_class(socket)
                                    #
         audionodesSocket.py        # for Audionodes
         audaspaceSocket.py         # for audaspace
         libspatialaudioSocket.py   # for libspatialaudio
         sdtSocket.py               # for Sound Design Toolkit
         [moduleName]Socket.py      #
         commonSocket.py            # Sockets common to more [moduleName]

/[moduleName]/
         __init__.py                # definisce le classi per NodeCategory e registra i node_items come node_categories
                                    # registra le classi definite nei files locali
                                    # definisce l'eventuale gestione extra dedicata al modulo/lib/servizio
                                    #
         [moduleName]nodes.py       # classi dei nodi con Naming convention
         [moduleName]ffi.py         # eventuali lib c/c++/... per il modulo
         [moduleName]....py         #
