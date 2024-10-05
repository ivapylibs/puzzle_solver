#================================= defaults ================================
#
# @brief    Manage the tracking of puzzle pieces. 
#
# Consists of methods/functions that will construct default configurations
# or class instances for working with puzzles, usually on a black mat.
#
#================================= defaults ================================
#
# @file     defaults.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/12/08 [created]
#
#
#================================= defaults ================================

#===== Environment / Dependencies
#
import trackpointer.centroidMulti as tpcm



#============================= CfgCentMulti ============================
#
# Use to be centroidMulti_builtForPuzzles. Makes little sense to be in 
# that module.
#
def CfgCentMulti():
  """!
  @brief    Default configuration for multi-centroid track pointer applied to
            singulated puzzle pieces. 

  Will ignore built up pieces.  Should have single puzzle board that forms
  solution and not permit smaller build outs of individual elements.
  """

  puzzleCfg = tpcm.CfgCentMulti()
  puzzleCfg.measProps = True
  puzzleCfg.minArea = 200
  puzzleCfg.maxArea = 1500
  return puzzleCfg

#
#================================= defaults ================================
