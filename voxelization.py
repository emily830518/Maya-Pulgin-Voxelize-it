import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import voxelize_color as vxc

def voxelize_method2(mesh,voxelStep):
	select = OpenMaya.MSelectionList()
	dagPath = OpenMaya.MDagPath()
	
	select.add(mesh)
	select.getDagPath(0, dagPath)
	 
	Mesh = OpenMaya.MFnMesh( dagPath )
	bounds = Mesh.boundingBox()
	MIN = bounds.min()
	MAX = bounds.max()

	grpName = cmds.group(n=mesh+'voxel',empty=True)

	isTex,meshMat,meshTex = vxc.isTextureApplied(mesh)
	
	vid = []
	MAXSize=(((round(max(MAX.x,MAX.y,MAX.z)/voxelStep)-round(min(MIN.x,MIN.y,MIN.z)/voxelStep))+2)**2)*3
	initializeProgressWindow("voxelizing " + mesh, MAXSize)
	progress=0
	i = min(MIN.x,MIN.y,MIN.z) - voxelStep
	while i <= max(MAX.x,MAX.y,MAX.z) + voxelStep:
		j = min(MIN.x,MIN.y,MIN.z) - voxelStep
		while j <= max(MAX.x,MAX.y,MAX.z) + voxelStep:
			for axis in ["zSide", "ySide", "xSide"] :
				z = 0
				y = 0
				x = 0
				zOffset = 0
				zDir = 0
				yOffset = 0
				yDir = 0
				xOffset = 0
				xDir = 0
				if axis == "zSide" :
					x = i
					y = j
					zOffset = 10000
					zDir = -1
				elif axis == "ySide" :
					x = i
					z = j
					yOffset = 10000
					yDir = -1
				elif axis == "xSide" :
					y = i
					z = j
					xOffset = 10000
					xDir = -1
 
				raySource = OpenMaya.MFloatPoint( x+xOffset, y+yOffset, z+zOffset )
				rayDirection = OpenMaya.MFloatVector(xDir, yDir, zDir)
				space=OpenMaya.MSpace.kWorld
				MAXParam=99999999
				accelParams=Mesh.autoUniformGridParams()
				hitPoints = OpenMaya.MFloatPointArray()
 
				hit = Mesh.allIntersections(raySource,
								rayDirection,
								None,
								None,
								False,
								space,
								MAXParam,
								False,
								accelParams,
								False,
								hitPoints,
								None,
								None,
								None,
								None,
								None)
				progress+=1
				if not hit :
					continue
				for k in xrange(hitPoints.length()) :
	
					cubepx = round(hitPoints[k].x/voxelStep)*voxelStep
					cubepy = round(hitPoints[k].y/voxelStep)*voxelStep
					cubepz = round(hitPoints[k].z/voxelStep)*voxelStep
				
					cubeId = "%s%s%s" % (cubepx, cubepy, cubepz)

					if cubeId in vid :
						continue
					else :
						vid.append(cubeId)
						if(not updateProgressWindow(progress,MAXSize)):
							break
					if not isTex: 
						myCube = cmds.polyCube(w=voxelStep,h=voxelStep,d=voxelStep)[0]
						cmds.hyperShade(myCube,assign=meshMat)
					else:
						color = vxc.getPointColorFromTex(Mesh,meshTex,cubepx,cubepy,cubepz,voxelStep,axis)
						matType = cmds.objectType(meshMat)
						myMat = vxc.generateMat(color,matType)
						myCube = cmds.polyCube(w=voxelStep,h=voxelStep,d=voxelStep)[0]
						cmds.hyperShade(myCube,assign=myMat)
					cmds.parent(myCube, grpName)
					cmds.polyBevel(myCube, offset=voxelStep/50.0)
					cmds.setAttr(myCube+".translate", cubepx, cubepy, cubepz)
			j+= voxelStep
		i+=voxelStep

	killProgressWindow()
	cmds.hide(mesh)

def voxelize(mesh,voxelStep):
	select = OpenMaya.MSelectionList()
	dagPath = OpenMaya.MDagPath()
	
	select.add(mesh)
	select.getDagPath(0, dagPath)
	
	Mesh = OpenMaya.MFnMesh( dagPath )
	vertices = OpenMaya.MPointArray()
	Mesh.getPoints(vertices, OpenMaya.MSpace.kWorld)

	grpName = cmds.group(empty=True)
	
	vid = []
	initializeProgressWindow("voxelizing " + mesh, vertices.length())

	for i in xrange(vertices.length()) :
	
		cubepx = round(vertices[i].x/voxelStep)*voxelStep
		cubepy = round(vertices[i].y/voxelStep)*voxelStep
		cubepz = round(vertices[i].z/voxelStep)*voxelStep
	
		cubeId = "%s%s%s" % (cubepx, cubepy, cubepz)

		if cubeId in vid :
			continue
		else :
			vid.append(cubeId)
			if(not updateProgressWindow(i, vertices.length())):
				break

		myCube = cmds.polyCube(w=voxelStep,h=voxelStep,d=voxelStep)[0]
		cmds.parent(myCube, grpName)
		cmds.polyBevel(myCube, offset=voxelStep/50.0)
		cmds.setAttr(myCube+".translate", cubepx, cubepy, cubepz)

	killProgressWindow()
	cmds.hide(mesh)

# Progress window
def initializeProgressWindow(t, MAXSize):
    cmds.progressWindow(title=t, progress=0, max=MAXSize, isInterruptable=True)

def updateProgressWindow(i, MAXSize):
    if(cmds.progressWindow(q=True, ic=True)):
        return False
    else:
        cmds.progressWindow(e=True, pr=i, st=("Building: " + str(i) + "/" + str(MAXSize)))
        return True

def killProgressWindow():
    cmds.progressWindow(ep=True)
    print "Build Completed"

def main(voxelStep):
	try:
		mesh = cmds.ls(sl=True)[0]
	except IndexError:
		print "No mesh selected."
		window=cmds.window(title="Error!", width=250)
		cmds.columnLayout( adjustableColumn=True )
		cmds.text( label='')
		cmds.text( label='No mesh selected, please select a mesh!', align='center' )
		cmds.text( label='')
		cmds.button( label='OK',w=20,h=20, command=('cmds.deleteUI(\"' + window + '\", window=True)') )
		cmds.showWindow( window )
		return
	# freeze tranformation
	cmds.makeIdentity(mesh,apply=True, t=1, r=1, s=1, n=0)
	voxelize_method2(mesh,voxelStep)
	print "Voxel Size: %s\n"%voxelStep