from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBAttributeSpec, NWBDatasetSpec
from pynwb import register_class, get_class, load_namespaces
from hdmf.utils import docval, call_docval_func, getargs, get_docval
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb import NWBHDF5IO
from pynwb.file import MultiContainerInterface, NWBContainer
from pynwb.spec import NWBDatasetSpec
import numpy as np
import pynwb
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence
from pynwb.device import Device

#Blender surfaces (Directly repurposed from CorticalSurfaces)
 
name = 'MeshClasses'
ns_path = name + ".namespace.yaml"
ext_source = name + ".extensions.yaml"
ns_builder = NWBNamespaceBuilder('Extension for storing attributes of 3D meshes', "TanLab", version='0.1.0')

mesh_attributes = NWBGroupSpec(doc='Stores attributes of 3D meshes',
                        datasets=[
                            NWBDatasetSpec(doc='Faces for surface, indexes vertices', shape=(None, 3),
                                          name='faces', dtype='uint', dims=('face_number', 'vertex_index')),
                            NWBDatasetSpec(doc='Center of mass of mesh', shape=(3,),
                                          name='center_of_mass', dtype='float'),
                            NWBDatasetSpec(doc='Vertices for surface, points in 3D space', shape=(None, 3),
                                          name='vertices', dtype='float', dims=('vertex_number', 'xyz'))],
                        attributes = [                             
                            NWBAttributeSpec(doc='Volume of mesh', name='volume', dtype='float'),
                            NWBAttributeSpec(doc='Surface area of mesh', name='surface_area', dtype='float')],
                       neurodata_type_def='MeshAttributes',
                       neurodata_type_inc='NWBDataInterface')


mesh_plane_segmentation = NWBGroupSpec('A plane segmentation to store attributes of 3D meshes',
                            neurodata_type_inc='PlaneSegmentation',
                            neurodata_type_def='MeshPlaneSegmentation',
                            groups = [mesh_attributes])

ns_builder.add_spec(ext_source, mesh_plane_segmentation)

                            
#Writes YAML files
ns_builder.export(ns_path)
