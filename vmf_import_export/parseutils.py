"""General format:
versioninfo{
	5 kvs:
	editorversion: int
	editorbuild: int
	mapversion: int
	formatversion: int, seems to be hardcoded to 100
	prefab: bool stored as int
}

visgroups{
	n*visgroup n>=0
	where visgroup =
		name: string
		visgroupid: int
		color: int[3]
		n*visgroup n>=0 (recursive)
}

viewsettings{
	bSnapToGrid: bool stored as int
	bShowGrid: bool stored as int
	bShowLogicalGrid: bool stored as int
	nGridSpacing: int
	bShow3DGrid: bool stored as int
}

world{
	id: int
	mapversion: int
	classname: string
	skyname: string

	n*(solid | hidden | group) n>=0, maybe 1
	where solid = 
		id: int
		n*side n>=1
		editor 
		where side =
			id: int
			plane: float? (non-integer)[3][3] (vertex[3])
			material: path, string
			uaxis: float[4], float
			rotation: float
			lightmapscale: int
			smoothing_groups: int
			dispinfo:
			where dispinfo = 
				power: int
				startposition: float[3] (vertex)
				elevation: float
				subdiv: bool as int
				normals
				distances
				offsets
				offset_normals
				alphas
				triangle_tags
				allowed_verts

				where normals =
					row[n]: float[3n] n>=0
	
				distances = 
					row[n]: float[n] n>=0

				offsets =
					row[n]: float[3n] n>=0

				offset_normals = 
					row[n]: float[3n] n>=0

				alphas =
					row[n]: int[n] n>=0, vdc says it's a decimal

				triangle_tags =
					row[n]: n*(0|1|9)

				allowed_verts =
					10: int[n] n>=0

		editor =
			color: int[3]
			visgroupid: int
			groupid: int
			visgroupshown: int
			visgroupautoshown: int
			comments: string
			logicalpos: float[2]

	group =
		id: int
		editor

	hidden =
		solid
}

entity{
	id: int
	classname: string
	spawnflags: int
	connections:
	solid
	hidden
	origin: float[3]
	editor

	where connections =
		n*[Output String]: string, [Input String], string, float, bool as int n>=0

cameras{
	activecamera: int
	n*camera n>=0, if n=0 then activecamera = -1
	where camera =
		position: float[3]
		look: float[3]
}

(LEGACY) cordon{
	mins: float[3]
	maxs: float[3]
	active: bool as int
}

(>L4D) cordons{
	active: bool as int
	n*cordon
	where cordon =
		name: string
		active: bool as int
		box
		where box =
			mins: float[3]
			maxs: float[3]
}



"""


class 