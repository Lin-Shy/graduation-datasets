"""Independent static polyMesh geometry reader with an explicit binary layout.

Supports native scalar-width points, label lists and OF9 faceCompactList.
No dictionary execution; dynamic mesh topology must be audited separately.
"""
import math
import re
import struct
import hashlib


def centre_signature(centres):
    rows=sorted(','.join(format(x,'.9f').replace('-0.000000000','0.000000000') for x in p) for p in centres)
    return hashlib.sha256(('\n'.join(rows)+'\n').encode('ascii')).hexdigest()


def _header(path):
    data=path.read_bytes()
    m=re.search(rb'\bFoamFile\s*\{[^}]*\}',data)
    if not m:raise ValueError('mesh_header_missing')
    h=m[0].decode('ascii')
    binary=bool(re.search(r'format\s+binary\s*;',h))
    cls=re.search(r'class\s+(\w+)\s*;',h)
    return data,m.end(),binary,cls[1] if cls else None


def _list(data,pos,code,binary):
    # Comments occur between the FoamFile header and first list.
    while True:
        ws=re.match(rb'\s*(?://[^\n]*\n|/\*.*?\*/)',data[pos:],re.S)
        if not ws:break
        pos+=ws.end()
    m=re.match(rb'\s*(\d+)\s*\(',data[pos:])
    if not m:raise ValueError('mesh_list_missing')
    n=int(m[1]);start=pos+m.end()
    if binary:
        end=start+n*struct.calcsize(code)
        if data[end:end+1]!=b')':raise ValueError('mesh_binary_list_length')
        values=[x[0] for x in struct.iter_unpack(code,data[start:end])]
    else:
        end=data.find(b')',start)
        if end<0:raise ValueError('mesh_ascii_list_unterminated')
        values=[int(x) if code[-1] in 'iq' else float(x) for x in data[start:end].split()]
        if len(values)!=n:raise ValueError('mesh_ascii_list_length')
    return values,end+1


def read_mesh(folder,layout):
    if layout.get('byte_order') not in ('little','big') or layout.get('scalar_bits') not in (32,64) or layout.get('label_bits') not in (32,64):
        raise ValueError('mesh_binary_layout_not_frozen')
    endian='<' if layout['byte_order']=='little' else '>'
    label=endian+('i' if layout['label_bits']==32 else 'q')
    scalar=endian+('d' if layout['scalar_bits']==64 else 'f')
    data,pos,binary,cls=_header(folder/'points')
    if binary:
        # A vector list is contiguous triples, but its size counts vectors.
        m=re.search(rb'\n\s*(\d+)\s*\(',data[pos:])
        if not m:raise ValueError('mesh_points_missing')
        count=int(m[1]);start=pos+m.end();end=start+count*3*struct.calcsize(scalar)
        if data[end:end+1]!=b')':raise ValueError('mesh_points_binary_length')
        coords=[x[0] for x in struct.iter_unpack(scalar,data[start:end])]
    else:
        body=re.sub(rb'//[^\n]*|/\*.*?\*/',b'',data[pos:],flags=re.S)
        m=re.match(rb'\s*(\d+)\s*\(',body)
        if not m:raise ValueError('mesh_points_missing')
        count=int(m[1]);rows=re.findall(rb'\(([^()]*)\)',body[m.end():])
        coords=[float(x) for row in rows for x in row.split()]
        if len(coords)!=count*3:raise ValueError('mesh_points_ascii_length')
    if not all(math.isfinite(x) for x in coords):raise ValueError('nonfinite_mesh_points')
    points=[coords[i:i+3] for i in range(0,len(coords),3)]
    data,pos,binary,cls=_header(folder/'faces')
    if cls=='faceCompactList':
        offsets,pos=_list(data,pos,label,binary);indices,pos=_list(data,pos,label,binary)
        if not offsets or offsets[0]!=0 or offsets[-1]!=len(indices) or any(b-a<3 for a,b in zip(offsets,offsets[1:])):
            raise ValueError('mesh_face_offsets')
        faces=[indices[a:b] for a,b in zip(offsets,offsets[1:])]
    elif cls=='faceList' and not binary:
        body=re.sub(rb'//[^\n]*|/\*.*?\*/',b'',data[pos:],flags=re.S)
        m=re.match(rb'\s*(\d+)\s*\(',body)
        if not m:raise ValueError('mesh_faces_missing')
        faces=[]
        for n,row in re.findall(rb'(\d+)\s*\(([^()]*)\)',body[m.end():]):
            f=[int(x) for x in row.split()]
            if len(f)!=int(n) or len(f)<3:raise ValueError('mesh_face_length')
            faces.append(f)
        if len(faces)!=int(m[1]):raise ValueError('mesh_face_count')
    else:raise ValueError('unsupported_mesh_face_format')
    lists=[]
    for name in ('owner','neighbour'):
        data,pos,binary,cls=_header(folder/name);v,_=_list(data,pos,label,binary);lists.append(v)
    owner,neighbour=lists
    if len(owner)!=len(faces) or len(neighbour)>len(owner) or not owner:raise ValueError('mesh_addressing_count')
    if any(x<0 for x in owner+neighbour):raise ValueError('negative_cell_index')
    volumes=[0.]*(max(owner+neighbour)+1);moments=[[0.,0.,0.] for _ in volumes]
    for fi,face in enumerate(faces):
        if any(x<0 or x>=len(points) for x in face):raise ValueError('mesh_vertex_index')
        a=points[face[0]]
        for i in range(1,len(face)-1):
            b=points[face[i]];c=points[face[i+1]]
            cross=[b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0]]
            volume=sum(a[q]*cross[q] for q in range(3))/6
            cells=[(owner[fi],1)] + ([(neighbour[fi],-1)] if fi<len(neighbour) else [])
            for cell,sign in cells:
                volumes[cell]+=sign*volume
                for q in range(3):moments[cell][q]+=sign*volume*(a[q]+b[q]+c[q])/4
    if any(not math.isfinite(v) or v<=0 for v in volumes):raise ValueError('nonpositive_mesh_cell_volume')
    centres=[[x/v for x in moment] for moment,v in zip(moments,volumes)]
    return {'cell_volumes_m3':volumes,'cell_centres_m':centres,'cell_count':len(volumes),
            'point_count':len(points),'face_count':len(faces),'volume_m3':sum(volumes),
            'bounds_m':[[min(p[q] for p in points) for q in range(3)],
                        [max(p[q] for p in points) for q in range(3)]]}
