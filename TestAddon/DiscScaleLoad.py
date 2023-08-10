import numpy as np
import os
from pynwb import NWBFile, NWBHDF5IO, image
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, ImagingPlane
from pynwb.file import Subject
from pynwb.device import Device
import math

import statistics
import pandas as pd
import h5py #Provides methods to supplement NWB
import datajoint as dj #
import csv 
from datetime import datetime
from dateutil import tz
from pynwb import NWBHDF5IO
from matplotlib import pylab as plt


#from ClassDefinitions import Subject, Session, Image_segmentation, Dendrite

def connect_to_dj():
    dj.config['database.host'] = 'spinup-db001f1f.cluster-cyynsscieqtk.us-east-1.rds.amazonaws.com'
    dj.config['database.user'] = 'MarikeReimer'
    dj.config['database.password'] = 'uqHKL3YLMCG0'
    dj.conn()

    #Create a schema to organize the pipeline. Defining it here means you only need to change the code in one place.
    current_schema = dj.schema('MarikeReimer', locals())
    return current_schema


schema = connect_to_dj()
print(schema)
schema

#Define Mouse table
@schema
class Mouse(dj.Manual):
    definition = """
    subject_id: varchar(128)                  # Primary keys above the '---'
    ---
    #non-primary columns below the '---' 
    genotype: enum('B6', 'BalbC', 'Unknown', 'Thy1-YFP')
    sex: enum('M', 'F', 'Unknown')
    species: varchar(128)
    strain: varchar(128)
    """

@schema
class Session(dj.Manual):
    definition = """
    ->Mouse
    identifier: varchar(128)                  # Primary keys above the '---'
    ---
    #non-primary columns below the '---' 
    surgery: varchar(128)
    pharmacology: varchar(128)
    """


@schema
class Dendrite(dj.Manual):
    definition = """
    ->Session
    dendrite_id: int                  # Primary keys above the '---'
    ---
    #non-primary columns below the '---'
    soma_center_point: longblob
    proximal_dendrite_length: float
    medial_dendrite_length: float
    distal_dendrite_length: float
    """

@schema
class Image_segmentation(dj.Imported):
    definition = """
    ->Dendrite
    segmentation_name: varchar(128)                  # Primary keys above the '---'
    ---
    #non-primary columns below the '---'
    length: float
    volume: float
    surface_area:float
    spine_type: enum('mushroom', 'thin', 'disconnected', 'stubby','U')
    center_of_mass: longblob
    """
    def make(self, key):
        subject_id = key['subject_id']
        identifier = key['identifier']

        nwbfile_to_read = 'C:/Users/meowm/OneDrive/TanLab/DataJointTesting/NWBfiles/' + str(subject_id) + str(identifier) + '.nwb' #TODO: Remove hard coding
        #nwbfile_to_read = 'C:/Users/meowm/Downloads/NWBfiles/' + str(subject_id) + str(identifier) + '.nwb'

        print(nwbfile_to_read)
        with NWBHDF5IO(nwbfile_to_read, 'r') as io:
            nwbfile = io.read()     
            for group in nwbfile.processing["SpineData"]["ImageSegmentation"].children[:]:
                print(group.name)
                if group.name.startswith("Mushroom"):
                    spine_type = 'mushroom'
                elif group.name.startswith("Thin"):
                    spine_type = 'thin'
                elif group.name.startswith("Disconnected"):
                    spine_type = 'disconnected'
                elif group.name.startswith("Stubby"):
                    spine_type = 'stubby'
                else:
                    spine_type = 'U'

                print(spine_type)    
                length = nwbfile.processing["SpineData"]["ImageSegmentation"][group.name].length.data[:]
                length = length[0]
                volume = nwbfile.processing["SpineData"]["ImageSegmentation"][group.name].volume.data[:]
                volume = volume[0]
                surface_area = nwbfile.processing["SpineData"]["ImageSegmentation"][group.name].surface_area.data[:]
                surface_area = surface_area[0]
                center_of_mass = nwbfile.processing["SpineData"]["ImageSegmentation"][group.name].center_of_mass.data[:]
                center_of_mass = center_of_mass[0]
                
                key['segmentation_name'] = group.name 
                key['length'] = length
                key['volume'] = volume
                key['surface_area'] = surface_area
                key['spine_type'] = spine_type
                key['center_of_mass'] = center_of_mass
                self.insert1(key)

@schema
class Distance_to_soma(dj.Computed):
    definition = """
    ->Image_segmentation
    ---
    distance_to_soma: float"""
    def make(self, key):
        center_of_mass = (Image_segmentation() & key).fetch1('center_of_mass')
        soma_center_point = (Dendrite() & key).fetch1('soma_center_point')
        distance_to_soma = math.dist(center_of_mass,soma_center_point)

        key['distance_to_soma'] = distance_to_soma
        self.insert1(key)

#Instantiate tables
mouse = Mouse()
session = Session()
dendrite = Dendrite()
image_segmentation = Image_segmentation()
distance_to_soma = Distance_to_soma()


path = 'C:/Users/meowm/OneDrive/TanLab/DataJointTesting/' #TODO: remove hard coding
#path = 'C:/Users/meowm/Downloads/'

os.chdir(path)
#Read in dendrite data from CSV
with open('DataJointDiscDendriteTable_V1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader) # This skips the header row of the CSV file.
    #Make a list of the NWB files in the directory
    # path = 'C:/Users/meowm/OneDrive/TanLab/DataJointTesting/NWBFiles'
    # os.chdir(path)
    nwb_file_path = 'C:/Users/meowm/OneDrive/TanLab/DataJointTesting/NWBfiles/'
    os.chdir(nwb_file_path)
    NWBfiles = os.listdir(nwb_file_path)
    NWBfiles.sort()
    
    for row in csv_reader:
        subject_id = str(row[0])
        identifier = row[1]

        nwb_filename = subject_id + identifier + '.nwb'
        print(nwb_filename)

        dendrite_number = float(row[2])

        soma_center_pointX = float(row[3])
        soma_center_pointY = float(row[4])
        soma_center_pointZ = float(row[5])
        soma_center_point = [soma_center_pointX, soma_center_pointY, soma_center_pointZ]
        soma_center_point = np.asarray(soma_center_point)

        proximal_dendrite_length = float(row[6])
        medial_dendrite_length = float(row[7])
        distal_dendrite_length = float(row[8])
        

        print(nwb_filename)
        with NWBHDF5IO(nwb_filename, 'r') as io:
            nwbfile = io.read()
        
        #Subject fields
        genotype = nwbfile.subject.genotype
        sex = nwbfile.subject.sex
        species = nwbfile.subject.species
        strain = nwbfile.subject.strain
        subject_id = nwbfile.subject.subject_id

        #NWBFile Fields
        identifier = nwbfile.identifier
        pharmacology = nwbfile.pharmacology
        surgery = nwbfile.surgery

        mouse.insert1((
            subject_id,
            genotype,
            sex,   
            species,
            strain
            ), skip_duplicates = True)  

        session.insert1((
            subject_id,
            identifier,
            surgery,
            pharmacology
        ))

        dendrite.insert1((
            subject_id,
            identifier,
            dendrite_number,
            soma_center_point,
            proximal_dendrite_length,
            medial_dendrite_length,
            distal_dendrite_length
        ))

        image_segmentation.populate()
        distance_to_soma.populate()
print("Data loaded")