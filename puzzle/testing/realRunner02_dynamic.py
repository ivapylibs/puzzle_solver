#!/usr/bin/python
"""

    @brief:             Test and update the puzzle solver planner function on the real world data.
                        The motivation for this test series is the limit of the performance stability in the real system testing scenerio.
                        Hence, this can be treated as an augmentation of the previous real-world unit test for the robustness.

                        The test focuses on the puzzle solving planner, rather than the activity-related functions.

                        This script test on the the case involving the view blocking simulatled by the black paper.
    
    @author:            Yiye Chen,          yychen2019@gatech.edu
    @date:              08/01/2022[created]

"""

# ===[0] prepare Dependencies
from argparse import ArgumentParser
import os, sys
from tqdm import tqdm
from copy import deepcopy

import rosbag
from cv_bridge import CvBridge
import matplotlib.pyplot as plt
import cv2

# display
from camera.utils.display import display_images_cv

# surveillance
from utils.survRunner import SurvRunner

# puzzle solver
from puzzle.piece.template import Template
from puzzle.runner import ParamRunner, RealSolver
from puzzle.simulator.basic import Basic

# ===[1] Get arguments
def get_args():
    parse = ArgumentParser("The arguments for the puzzle solving planner real world unit test")
    parse.add_argument("--root_data_folder", type=str, default="./data_rosbag/Testing/Yiye/robot_puzzle",
                        help="The root of the rosbag test data.")
    #parse.add_argument("--piece_num", default=9, type=int, 
    #                    help="The number of pieces. For determining the test cases")
    #parse.add_argument("--shuffleRot", action="store_true",
    #                    help="Add shuffle and rotation or not. For determining the test cases")

    args = parse.parse_args()
    return args

def parse_args(args):
    #args.sol_path = os.path.join(args.data_folder, "sol{}.obj".format(args.piece_num))
    #post_fix = "noShuffleRot" if not args.shuffleRot else "yesShuffleRot"
    #args.test_data_path = os.path.join(args.data_folder, "static_{}.bag".format(post_fix))

    args.planOnTrack=True

    # NOTE: add "_B" due to the recalibration of the system.
    args.data_folder = os.path.join(args.root_data_folder, "pieces_20")
    args.test_data_path = os.path.join(args.data_folder, "dynamic_blockShuffle_B.bag")
    args.sol_path = os.path.join(args.data_folder, "sol20_B.obj")

    return args

args = get_args()
args = parse_args(args)

# ===[2] Prepare data
bridge = CvBridge()
test_rosbag = rosbag.Bag(args.test_data_path)
test_data_path = args.test_data_path
sol_path = args.sol_path

# get the depth scale
depth_scale = None
for topic, msg, t in test_rosbag.read_messages(["/depth_scale"]):
    depth_scale = msg.data
assert depth_scale is not None, "Depth scale is not read."

# get an example data
rgb_example = None
dep_example = None
for topic, msg, t in test_rosbag.read_messages(["/test_rgb", "/test_dep"]):
    if topic == "/test_rgb":
        rgb_example = bridge.imgmsg_to_cv2(msg)[:,:,::-1]
    elif topic == "/test_dep":
        dep_example = bridge.imgmsg_to_cv2(msg) * depth_scale
    
    if rgb_example is not None and dep_example is not None:
        break


# ===[3] Prepare the models 

# surveillance for obtaining the puzzle layer
surv_args = {
    "rgb_topic": "/test_rgb",
    "dep_topic": "/test_dep",
    "reCalibrate": False,
    "calib_data_path": test_data_path 
}
surv_runner = SurvRunner(surv_args=surv_args)

# puzzle solver
configs_puzzleSolver = ParamRunner(
    areaThresholdLower=1000, # @< The area threshold (lower) for the individual puzzle piece.
    areaThresholdUpper=8000, # @< The area threshold (upper) for the individual puzzle piece.
    pieceConstructor=Template,
    lengthThresholdLower=1000,
    BoudingboxThresh=(20, 100), # @< The bounding box threshold for the size of the individual puzzle piece.
    tauDist=100, # @< The radius distance determining if one piece is at the right position.
    hand_radius=200, # @< The radius distance to the hand center determining the near-by pieces.
    tracking_life_thresh=15, # @< Tracking life for the pieces, it should be set according to the processing speed.
    # solution_area=[600,800,400,650], # @< The solution area, [xmin, xmax, ymin, ymax]. We will perform frame difference in this area to locate the touching pieces.
    # It is set by the calibration result of the solution board.
)
puzzle_solver = RealSolver(configs_puzzleSolver)

# puzzle solver - set solution board
puzzle_solver.setSolBoard(rgb_example, sol_path)

solImg = puzzle_solver.bSolImage
plt.figure()
plt.title("The solution board")
plt.imshow(solImg)
plt.pause(1)
# assert the solution board coordinate is assigned correctly. In some cases it maps multiple pieces to a same coordinate.
solBoard = puzzle_solver.getSolBoard()
print(solBoard.getGc())
if not solBoard.assert_gc(verbose=True):
    print("GC assignment incorrect")
    exit()
else:
    print("GC assignment is good.")


# ===[4] Run
rgb = None
dep = None

# prepare plt.figures
fh, (ax1_sv, ax2_sv) = plt.subplots(1, 2)
fh.tight_layout()
fh.suptitle("The Surveillance system")
fh2, (ax1_ps, ax2_ps, ax3_ps) = plt.subplots(1, 3)
fh2.suptitle("The puzzle solver.")
fh2.tight_layout()

tqdm_bar = tqdm(total=test_rosbag.get_message_count(topic_filters=["/test_rgb"]))
for topic, msg, t in test_rosbag.read_messages(["/test_rgb", "/test_depth"]):
    tqdm_bar.update(1)

    # ----- Read data
    if topic == "/test_rgb":
        rgb = bridge.imgmsg_to_cv2(msg)
    elif topic == "/test_depth":
        dep = bridge.imgmsg_to_cv2(msg) * depth_scale

    # if either is None, then continue to read data 
    if rgb is None or dep is None: 
        continue
    
    # ----- If obtained both modalities, process the data

    # surveillance
    surv_runner.process(rgb, dep)

    # get the puzzle layer info
    puzzle_mask = surv_runner.surv.scene_interpreter.get_layer("puzzle", mask_only=True, BEV_rectify=False)
    puzzle_layer = surv_runner.surv.scene_interpreter.get_layer("puzzle", mask_only=False, BEV_rectify=False)
    puzzle_layer_BEV = surv_runner.surv.scene_interpreter.get_layer("puzzle", mask_only=False, BEV_rectify=True)
    puzzle_trackers = surv_runner.surv.scene_interpreter.get_trackers("puzzle", BEV_rectify=False)
    human_layer = surv_runner.surv.scene_interpreter.get_layer("human", mask_only=False, BEV_rectify=False)

    # plan
    postImg = surv_runner.surv.meaBoardImg
    visibleMask = surv_runner.surv.visibleMask
    hTracker_BEV = surv_runner.surv.scene_interpreter.get_trackers("human", BEV_rectify=True)  # (2, 1)
        
    plans = puzzle_solver.process(postImg, visibleMask, hTracker_BEV, verbose=False, debug=False, planOnTrack=args.planOnTrack)

    # simulate the plan
    meaBoard = puzzle_solver.getMeaBoard()
    trackBoard = puzzle_solver.getTrackBoard()
    if args.planOnTrack:
        boardPlan = trackBoard 
    else:
        boardPlan = meaBoard
    theSim = Basic(deepcopy(boardPlan))
    for plan in plans:
        theSim.takeAction([plan], verbose=False)
    img_assemble = theSim.toImage(ID_DISPLAY=True)


    # -- print key information for debugging
    print("The correspondence detected by the manager: \n {}".format(puzzle_solver.theManager.pAssignments))
    print("The rotations detected by the manager: \n {}".format(puzzle_solver.theManager.pAssignments_rotation))
    # print("The track board adjacency matrix: \n {}".format(trackBoard.adjMat))    # NOTE: 


    # -- visualization for debugging

    # the surveillance system 
    ax1_sv.imshow(rgb)
    ax1_sv.set_title("THe test rgb frame")
    ax2_sv.imshow(puzzle_layer)
    ax2_sv.set_title("THe extracted puzzle layer")

    # the puzzle solver
    ax1_ps.imshow(meaBoard.toImage(ID_DISPLAY=True))
    ax1_ps.set_title("THe measure board")
    ax2_ps.imshow(trackBoard.toImage(ID_DISPLAY=True))
    ax2_ps.set_title("THe tracking board")
    ax3_ps.imshow(img_assemble)
    ax3_ps.set_title("THe simulated assembly result")

    plt.pause(1)
    # plt.show()

    # reset
    rgb = None
    dep = None
    