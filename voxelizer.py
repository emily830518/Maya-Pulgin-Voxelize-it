import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
from functools import partial
import voxelization

kPluginCmdName = "voxelizeit"
voxelStep=1.0

def start(*args):
    voxelization.main(voxelStep)


# Command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    # Invoked when the command is run.
    def doIt(self,argList):
        # Start with the Window
        cmds.window(title="Voxelize it!", width=150)
        cmds.columnLayout( adjustableColumn=True )
        cmds.image( image='/Users/Emily/Desktop/New York University/Adv CG/voxelizeiticon.png', bgc=[1.0,1.0,1.0])
        self.slider=cmds.floatSliderGrp( label='Voxel Size', field=True, minValue=0.01, maxValue=10.00, value=1.00 , cc=self.update_slider_value, precision=2)
        cmds.button( label='RUN',command = start)
        cmds.showWindow()
    
    def update_slider_value(self,*arg):
        global voxelStep
        voxelStep = cmds.floatSliderGrp(self.slider, q=True, v=True)


# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( scriptedCommand() )
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )