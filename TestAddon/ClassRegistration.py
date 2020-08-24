from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBAttributeSpec, NWBDatasetSpec
from pynwb import register_class, get_class, load_namespaces
from hdmf.utils import docval, call_docval_func, getargs, get_docval
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb import NWBHDF5IO
from pynwb.file import MultiContainerInterface, NWBContainer

load_namespaces('MeshClasses.namespace.yaml')

@register_class('MeshAttributes', 'TanLab')
class MeshAttributes(NWBContainer):
    __nwbfields__ = (
        'faces',
        'verticies',
        'center_of_mass',
        'volume',
        'surface_area'
        )

    @docval({'name': 'name', 'type': str, 'doc': 'name of this MeshAttributes'},
            {'name': 'faces', 'type': ('array_data', 'data'),'doc': 'faces for this surface', 'default': None}, 
            {'name': 'vertices', 'type': ('array_data', 'data'),'doc': 'vertices for this surface', 'default': None},
            {'name': 'center_of_mass', 'type': ('array_data', 'data'),'doc': 'surface center of mass', 'default': None},
            {'name': 'volume', 'type': float,'doc': 'surface volume', 'default': None},
            {'name': 'surface_area', 'type': float,'doc': 'surface center of mass', 'default': None}
            )
           
    def __init__(self, **kwargs):
        call_docval_func(super((MeshAttributes, self).__init__, kwargs))
        self.faces = getargs('faces', kwargs)
        self.vertices = getargs('vertices', kwargs)
        self.center_of_mass = getargs('center_of_mass', kwargs)
        self.volume = getargs('volume', kwargs)
        self.surface_area = getargs('surface_area', kwargs)
    