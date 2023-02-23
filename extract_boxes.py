import os
import argparse

import numpy as np
import open3d as o3d

from nuscenes.nuscenes import NuScenes

from log_handler import Logger, LogTemplates

logger = Logger(__name__)
CAR_BOX = "vehicle.car"


def load_scene_data(scene_number: int) -> tuple[np.ndarray, list]:
    """Loads the scene with neccessary data from NuScenes mini dataset.
    Converting coordinates of points in the array from absolute to relative.

    Args:
        scene_number (int): the number of scene in the dataset

    Returns:
        tuple[np.ndarray, list]: array of XYZ coordinates of points and
            list of boxes objects.
    """
    nusc = NuScenes(version='v1.0-mini', dataroot='NuScenes')
    logger.info(LogTemplates.LOADING_SCENE.format(scene_number))

    # Loading sample data.
    scene_token = nusc.scene[scene_number]['token']
    logger.info(LogTemplates.LOADING_SCENE_DATA.format(scene_token))
    sample_token = nusc.get('scene', scene_token)['first_sample_token']
    sample = nusc.get('sample', sample_token)

    # Loading lidar data.
    lidar_token = sample['data']['LIDAR_TOP']
    logger.info(LogTemplates.LOADING_LIDAR_DATA.format(lidar_token))
    lidar_data = nusc.get('sample_data', lidar_token)

    # Loading translation data.
    metadata = nusc.get('sample_data', lidar_token)['ego_pose_token']
    ego_pose_data = nusc.get('ego_pose', metadata)
    translation = ego_pose_data['translation']
    logger.info(LogTemplates.TRANSLATION.format(translation))

    # Loading points data.
    filepath = os.path.join(nusc.dataroot, lidar_data['filename'])
    logger.info(LogTemplates.LOADING_FROM_FILE.format(filepath))
    pc = np.fromfile(filepath, dtype=np.float32).reshape(-1, 5)[:, :3]
    logger.info(LogTemplates.LOADED_POINTS_ARRAY.format(pc.shape[0]))

    # Correcting coordinates for the points with translation data.
    pc = np.abs(pc - translation)

    # Loading boxes data.
    boxes = nusc.get_boxes(lidar_token)
    logger.info(LogTemplates.LOADED_BOXES.format(len(boxes)))
    return pc, boxes


def extract_boxes(boxes: list, pc: np.ndarray, box_name: str):
    """Iterates over a list of boxes and found objects with specified name.
    Founding points, which are inside of the box with mask, writes clouds of
    points into the file.

    Args:
        boxes (list): list of the boxes objects in the scene.
        pc (np.ndarray): array of relative XYZ coordinates of the points
        box_name (str): the name of the box objects to work with
    """
    for idx, box in enumerate(boxes):
        if box.name != CAR_BOX:
            continue
        logger.info(LogTemplates.FOUND_BOX.format(box_name))

        # Reading center coordinates of the box.
        center = box.center
        logger.info(LogTemplates.BOX_CENTER.format(center.tolist()))

        # Reading dimensions of the box.
        width = box.wlh[0]
        length = box.wlh[1]
        height = box.wlh[2]
        logger.info(LogTemplates.BOX_SIZES.format([width, length, height]))

        x, y, z = pc[:, 0], pc[:, 1], pc[:, 2]
        # Creating a mask for points, which are supposed to be in the box.
        mask = ((x >= center[0] - width / 2) & (x <= center[0] + width / 2) &
                (y >= center[1] - length / 2) & (y <= center[1] + width / 2) &
                (z >= center[2] - height / 2) & (z <= center[2] + height / 2))

        # Applying the mask to the points array.
        pc_car = pc[mask]

        if len(pc_car) > 0:
            filename = f'car_{idx}.ply'
            # Writing cloud of points into the file.
            o3d.io.write_point_cloud(filename, o3d.geometry.PointCloud(
                points=o3d.utility.Vector3dVector(pc_car)))

            # Adding name of the file to the result list (for the logger).
            result_files.append(filename)
            logger.info(LogTemplates.WRITED_FILE.format(len(pc_car)))
        else:
            logger.warning(LogTemplates.NO_POINTS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts clouds of points"
                                     "inside of the car boxes.")
    # Reading arguments from the command line.
    parser.add_argument("--scene_number", type=int,
                        help="number scene to load (between 0 and 9)")
    args = parser.parse_args()
    if args.scene_number not in range(10):
        logger.error(LogTemplates.WRONG_SCENE)
    else:
        global result_files
        result_files = []
        pc, boxes = load_scene_data(args.scene_number)
        extract_boxes(boxes, pc, CAR_BOX)
        logger.info(LogTemplates.FINISHED.format(len(result_files),
                                                 result_files))
