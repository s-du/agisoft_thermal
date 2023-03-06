# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 15:55:23 2023

@author: sdu (Buildwise)
This code allows to process thermal images with Agisoft Metashape Module
"""

import os
from pathlib import Path

# get license
license_path = r'C:\Program Files\Agisoft\Metashape Pro\metashape2.lic'
os.environ['agisoft_LICENSE'] = str(Path(license_path))
print('Here it is!!', os.environ['agisoft_LICENSE'])

# import modules
import subprocess
import sys
import pkg_resources


# general parameters
DOWN_SCALE = 1

# paths
basepath = os.path.dirname(__file__)
PSX_PATH = 'agisoft.psx'
RGB_IMG_FOLDER = os.path.join(basepath,'test_dataset', 'rgb')
IR_IMG_FOLDER = os.path.join(basepath,'test_dataset', 'thermal')
METASHAPE_MODULE_PATH = os.path.join(basepath,'tools','Metashape-2.0.0-cp35.cp36.cp37.cp38-none-win_amd64.whl')

"""
AGISOFT MODULE INSTALLATION PROCEDURE___________________________________________________________________________________
"""
def install_agisoft_module():
    # install Metashape module if necessary
    def install(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    metashape_module = METASHAPE_MODULE_PATH
    install(metashape_module)

# check if module is installed
required = {'metashape'}
installed = {pkg.key for pkg in pkg_resources.working_set}
print(installed)
missing = required - installed
if missing:
    print(r"Ok let's intall Agisoft!")
    install_agisoft_module()

import Metashape

"""
GENERAL METHODS_________________________________________________________________________________________________________
"""

def run_agisoft_thermal(ir_img_folder, rgb_img_folder):
    # create agisoft document
    doc = Metashape.Document()
    doc.save(path=PSX_PATH)
    # create chunk
    chk = doc.addChunk()
    # add the ir and rgb pictures
    #   loading RGB images
    image_list = os.listdir(rgb_img_folder)
    rgb_list = []
    for img in image_list:
        rgb_list.append(os.path.join(rgb_img_folder, img))

    # load thermal images
    image_list = os.listdir(ir_img_folder)
    ir_list = []
    for img in image_list:
        ir_list.append(os.path.join(ir_img_folder, img))


    images = [None] * (len(rgb_list) + len(ir_list))
    images[::2] = rgb_list
    images[1::2] = ir_list
    filegroups = [2] * (len(images) // 2)
    # images is alternating list of rgb, ir paths
    # filegroups defines the multi-camera system groups: [2, 2, 2, ....]

    chk.addPhotos(filenames=images, filegroups=filegroups, layout=Metashape.MultiplaneLayout)
    print('photos added!')

    # check master
    for sensor in chk.sensors:
        if sensor == sensor.master:
            continue
        print(sensor.label)

    # align photos (based on rgb data)
    chk.matchPhotos(downscale=DOWN_SCALE)
    chk.alignCameras()
    doc.save(path=PSX_PATH)

def compute_camera_path(model_path, output_psx_path):
    doc = Metashape.Document()
    doc.open(path='agisoft_ref_file.psx')

    chk = doc.chunk
    chk.importModel(path=model_path, format=Metashape.ModelFormatOBJ)

    plan_mission_task = Metashape.Tasks.PlanMission()
    # mission parameters
    plan_mission_task.sensor = 0  # choose the camera that was used for input photos
    plan_mission_task.min_altitude = 10
    plan_mission_task.capture_distance = 6
    plan_mission_task.horizontal_zigzags = True
    plan_mission_task.min_waypoint_spacing = 0.5
    plan_mission_task.overlap = 50
    plan_mission_task.attach_viewpoints = True
    plan_mission_task.safety_distance = 1

    plan_mission_task.apply(chk)
    doc.save(path=output_psx_path)

# Run
run_agisoft_thermal(IR_IMG_FOLDER, RGB_IMG_FOLDER)

