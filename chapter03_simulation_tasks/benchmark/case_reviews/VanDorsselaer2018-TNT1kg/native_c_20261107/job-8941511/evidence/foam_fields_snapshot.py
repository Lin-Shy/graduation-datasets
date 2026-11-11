"""Read scalar/vector field values, including native OpenFOAM binary lists.

Binary layouts must be declared in the header or frozen by the operator. No
host-native guessing, executable dictionary expansion, or solver invocation.
"""
from __future__ import annotations
import math
import re
import struct


def read_internal_volume_scalar(path, binary_layout=None):
    """Read OF volScalarField::Internal without weakening full-field validation.

    The native internal-only format uses `value`, unlike a volScalarField's
    `internalField`. Translate that one textual keyword in memory, preserving
    the declared binary layout and every payload byte. Never change the file.
    """
    raw=path.read_bytes()
    token=re.compile(rb'//[^\n]*(?:\n|$)|/\*.*?\*/|\bvalue\s+(uniform|nonuniform)\s+',re.S)
    first=next((m for m in token.finditer(raw) if m[1] is not None),None)
    if first is None:raise ValueError('missing_internal_volume_scalar_value')
    header=re.sub(rb'/\*.*?\*/|//[^\n]*',b'',raw[:first.start()],flags=re.S)
    if not re.search(rb'\bclass\s+volScalarField::Internal\s*;',header):
        raise ValueError('not_declared_internal_volume_scalar')
    transformed=raw[:first.start()]+b'internalField'+raw[first.start()+len(b'value'):]
    class MemoryField:
        def read_bytes(self):return transformed
    result=read_field(MemoryField(),binary_layout)
    result['native_class']='volScalarField::Internal'
    return result


def read_field(path, binary_layout=None):
    raw=path.read_bytes()
    # Comment tokens are recognised only in textual regions. The scanner jumps
    # over binary payloads before looking for any subsequent keyword/comment.
    token=re.compile(rb'//[^\n]*(?:\n|$)|/\*.*?\*/|\b(internalField|value|refValue|refGradient|valueFraction)\s+(uniform|nonuniform)\s+',re.S)
    first=next((m for m in token.finditer(raw) if m[1] is not None),None)
    if first is None or first[1]!=b'internalField':raise ValueError('missing_internal_field')
    header_end=first.start()
    header=raw[:header_end].decode('ascii')
    header=re.sub(r'/\*.*?\*/|//[^\n]*','',header,flags=re.S)
    binary=bool(re.search(r'\bformat\s+binary\s*;',header))
    layout=None
    if binary:
        arch=re.search(r'\barch\s+"(LSB|MSB);label=(32|64);scalar=(32|64)"',header)
        if arch:
            layout={'byte_order':'little' if arch[1]=='LSB' else 'big',
                    'label_bits':int(arch[2]),'scalar_bits':int(arch[3])}
            if binary_layout is not None and binary_layout!=layout:raise ValueError('binary_layout_mismatch')
        else:layout=binary_layout
        if not layout or layout.get('byte_order') not in {'little','big'} or layout.get('scalar_bits') not in {32,64} or layout.get('label_bits') not in {32,64}:
            raise ValueError('binary_layout_not_frozen')
    # Scan textual tokens; jump over exactly sized raw payloads.
    pos=header_end;internal=None;all_values=[];internal_count=None
    while match:=token.search(raw,pos):
        if match[1] is None:
            pos=match.end();continue
        kind=match[1];start=match.end()
        if match[2]==b'uniform':
            end=raw.find(b';',start)
            if end<0:raise ValueError('unterminated_uniform_field')
            value=re.sub(r'/\*.*?\*/|//[^\n]*','',raw[start:end].decode('ascii'),flags=re.S).strip()
            values=[float(x) for x in value.strip('()').split()]
            if len(values) not in {1,3}:raise ValueError('unsupported_uniform_components')
            count=1;pos=end+1
        else:
            empty=re.match(rb'List<(scalar|vector)>\s+0\s*;',raw[start:])
            if empty:
                # OF9 writes a zero-face patch as "List<scalar> 0;", without
                # parentheses. This is valid on a boundary, never internally.
                if kind==b'internalField':raise ValueError('empty_internal_field')
                pos=start+empty.end();continue
            spec=re.match(rb'List<(scalar|vector)>\s+(\d+)\s*\(',raw[start:])
            if not spec:raise ValueError('unparsed_nonuniform_field')
            components=1 if spec[1]==b'scalar' else 3
            count=int(spec[2]);payload=start+spec.end()
            if binary:
                size=layout['scalar_bits']//8;end=payload+count*components*size
                if end>len(raw) or raw[end:end+1]!=b')':raise ValueError('binary_field_length_mismatch')
                fmt=('<' if layout['byte_order']=='little' else '>')+('d' if size==8 else 'f')
                values=[x[0] for x in struct.iter_unpack(fmt,raw[payload:end])]
            else:
                end=raw.find(b')',payload) if components==1 else raw.find(b';',payload)
                if end<0:raise ValueError('unterminated_ascii_list')
                body=re.sub(r'/\*.*?\*/|//[^\n]*','',raw[payload:end].decode('ascii'),flags=re.S)
                values=[float(x) for x in body.replace('(',' ').replace(')',' ').split()]
                if len(values)!=count*components:raise ValueError('field_length_mismatch')
            pos=end+1
        if not all(math.isfinite(x) for x in values):raise ValueError('nonfinite_field')
        all_values.extend(values)
        if kind==b'internalField':
            if internal is not None:raise ValueError('duplicate_internal_field')
            internal=values;internal_count=count
    if not internal:raise ValueError('empty_internal_field')
    dims=re.search(r'\bdimensions\s+\[([^]]+)\]',header)
    return {'internal':internal,'all_values':all_values,'count':internal_count,
            'dimensions':[int(x) for x in dims[1].split()] if dims else None,
            'binary_layout':layout}
