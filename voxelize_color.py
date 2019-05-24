import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

color_table = dict()

# return whether there is a texture on the selected mesh and the texture name on it
def isTextureApplied(selectMesh):
	# get material attached on mesh
	mesh = cmds.ls(selectMesh, s=1, dag=1)[0]
	SgNodes = cmds.listConnections(mesh, type='shadingEngine')
	matMaya = cmds.listConnections(SgNodes [0] + '.surfaceShader')[0]
	# check whether the material has texture
	tex = cmds.defaultNavigation(dtv=True, destination=matMaya+'.color')
	if tex==[]:
		return False,matMaya,''
	return True,matMaya,tex[0]

# return the the most common color of texture around (px,py,pz)
def getPointColorFromTex(Mesh,Tex,px,py,pz,v_size,axis):
	color_list = dict()
	# collecting all voxel cube points
	pts=[]
	pts.append((px,py,pz))
	half = v_size/4.0
	if axis == "zSide":
		pts.append((px-half,py-half,pz))
		pts.append((px-half,py+half,pz))
		pts.append((px-half,py,pz))
		pts.append((px+half,py-half,pz))
		pts.append((px+half,py+half,pz))
		pts.append((px+half,py,pz))
		pts.append((px,py+half,pz))
		pts.append((px,py-half,pz))
	elif axis == "ySide":
		pts.append((px-half,py,pz-half))
		pts.append((px-half,py,pz+half))
		pts.append((px-half,py,pz))
		pts.append((px+half,py,pz-half))
		pts.append((px+half,py,pz+half))
		pts.append((px+half,py,pz))
		pts.append((px,py,pz+half))
		pts.append((px,py,pz-half))
	elif axis == "xSide":
		pts.append((px,py-half,pz-half))
		pts.append((px,py-half,pz+half))
		pts.append((px,py-half,pz))
		pts.append((px,py+half,pz-half))
		pts.append((px,py+half,pz+half))
		pts.append((px,py+half,pz))	
		pts.append((px,py,pz+half))
		pts.append((px,py,pz-half))

	for pt in pts:
		hitpt = OpenMaya.MPoint(pt[0],pt[1],pt[2])
		util = OpenMaya.MScriptUtil()
		uvPoint = util.asFloat2Ptr()
		Mesh.getUVAtPoint(hitpt, uvPoint, OpenMaya.MSpace.kWorld)
		u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
		v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)
		color = tuple(cmds.colorAtPoint( Tex, o='RGB', u=u, v=v ))
		if color in color_list:
			if pt[0]==px and pt[1]==py and pt[2]==pz:
				color_list[color]+=6;
			color_list[color]+=1;
		else:
			if pt[0]==px and pt[1]==py and pt[2]==pz:
				color_list[color]=7;
			else:
				color_list[color]=1;
	# print color_list
	return max(color_list, key=color_list.get)
	# hitpt = OpenMaya.MPoint(px,py,pz)
	# util = OpenMaya.MScriptUtil()
	# uvPoint = util.asFloat2Ptr()
	# Mesh.getUVAtPoint(hitpt, uvPoint, OpenMaya.MSpace.kWorld)
	# u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
	# v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)
	# color = cmds.colorAtPoint( Tex, o='RGB', u=u, v=v )
	# return tuple(color)

def generateMat(color,matType):
	if color not in color_table:
		myMat = cmds.shadingNode(matType, asShader=True)
		cmds.setAttr(myMat+'.color',color[0],color[1],color[2],type='double3')
		color_table[color]=myMat
		return myMat
	else:
		return color_table[color]

# def getVertexColr(hitPoint,Mesh, &R, &G, &B):
# 	 # get closest vertex on the Mesh
# 	 space = OpenMaya.MSpace.kWorld
# 	 closestPoint = OpenMaya.MPoint(0,0,0)
# 	 Mesh.getClosestPoint(hitPoint,closestPoint, space)
# 	 # get the vertex's uv coordinatesfloat2