import json
import re


def __insert_or_append(dic, key, value):
    if key not in dic:
        dic[key] = [value]
    else:
        dic[key].append(value)


def __logger(in_path, out_path, pattern, processor=None):
    in_file = open(in_path, 'r')
    out_file = open(out_path, 'w')
    p = re.compile(pattern)
    for line in in_file:
        j = json.loads(line)
        if not p.match(j['message']):
            continue
        if processor:
            out_file.write(processor(j))
        else:
            out_file.write(str(j).replace('\'', '"') + '\n')


def __processor(in_path, msg_heading):
    info = {}
    in_file = open(in_path, 'r')
    for line in in_file:
        j = json.loads(line)
        msg, pid = j['message'], int(j['process'])

        record = {}
        for field in msg[len(msg_heading):].split(', '):
            [key, value] = field.split('=')
            try:
                value_stored = int(value)
            except:
                value_stored = value
            info[key] = value_stored

        __insert_or_append(info, pid, record)

    return info


def __csv_gen(in_path, out_path, pid, fields, processor):
    info = processor(in_path)
    out = open(out_path, 'w')
    out.write(','.join(fields) + '\n')
    if pid not in info:
        raise ValueError(f"There is no record for pid {pid} in the file.")


    for item in info[pid]:
        out_line = ','.join([str(item[field]) for field in fields])
        out.write(out_line + '\n')


def clean(in_path, out_path):

    def process(j):
        j['timestamp'] = j['timestamp'].split(' ')[1][:-6]
        for field in ['level', 'tag', 'raw']:
            j.pop(field, None)
        return str(j).replace('\'', '"') + '\n'

    __logger(in_path, out_path, r'^\[HT\]', process)


def gc_filter(in_path, out_path):
    __logger(in_path, out_path, r'^\[HT\] \[GC\]')


def sys_gc_filter(in_path, out_path):
    __logger(in_path, out_path, r'^\[HT\] \[SysGC\]')


def heap_filter(in_path, out_path):
    __logger(in_path, out_path, r'^\[HT\] \[Heap\]')


def mem_filter(in_path, out_path):
    __logger(in_path, out_path, r'^\[HT\] \[((IPut)|(IGet))\]')


def __heap_processor(in_path):
    """
    Message format:
        [HT] [Heap] ts=...,
                    bytes_allocated=..., bytes_tl_bulk_allocated=..., heap_num_bytes_allocated=...,
                    art_obj_allocated=..., art_bytes_allocated=...
    Data format:
        { pid: {ts                      : int,  // unix-style timestamp
                bytes_allocated         : int,
                bytes_tl_bulk_allocated : int,
                heap_num_bytes_allocated: int,
                art_obj_allocated       : int,
                art_bytes_allocated     : int,
        }}
    """
    pid_heap = {}
    in_file = open(in_path, 'r')
    for line in in_file:
        l = json.loads(line)
        msg, pid = l['message'], int(l['process'])
        if msg.find('[HT] [Heap]') == -1:
            continue

        heap_alloc_info = {}
        for field in msg[12:].split(', '):
            [key, value] = field.split('=')
            heap_alloc_info[key] = int(value)

        __insert_or_append(pid_heap, pid, heap_alloc_info)

    return pid_heap


def __gc_processor(in_path):
    """
    Message format:
        [HT] [GC] [End] ts=...,
                        gc_cause=..., gc_name=...,
                        heap_obj_allocated=..., heap_bytes_allocated=...,
                        heap_obj_allocated_ever=..., heap_obj_freed_ever=..., heap_bytes_allocated_ever=..., heap_bytes_freed_ever=...,
                        gc_obj_freed=..., gc_bytes_freed=..., gc_large_obj_freed=..., gc_large_bytes_freed=...
    Data format:
        { pid: [{ ts                       : int,
                  tsh                      : int,
                  gc_cause                 : str,
                  gc_name                  : str,
                  heap_obj_allocated       : int,
                  heap_bytes_allocated     : int,
                  heap_obj_allocated_ever  : int,
                  heap_obj_freed_ever      : int,
                  heap_bytes_allocated_ever: int,
                  heap_bytes_freed_ever    : int,
                  gc_obj_freed             : int,
                  gc_bytes_freed           : int,
                  gc_large_obj_freed       : int,
                  gc_large_bytes_freed     : int,
        }]}
    """
    pid_gc = {}
    in_file = open(in_path, 'r')
    for line in in_file:
        l = json.loads(line)
        msg, pid = l['message'], int(l['process'])
        if msg.find('[HT] [GC] [End]') == -1:
            continue

        gc_info = {}
        for field in msg[16:].split(', '):
            [key, value] = field.split('=')
            try:
                value_stored = int(value)
            except:
                value_stored = value
            gc_info[key] = value_stored

        __insert_or_append(pid_gc, pid, gc_info)

    return pid_gc


def __mem_processor(in_path):
    """
    Message format
    Data format
    """
    pid_tid_mem = {}
    in_file = open(in_path, 'r')
    for line in in_file:
        l = json.loads(line)
        msg, pid, tid = l['message'], int(l['process']), int(l['thread'])
        if msg.find('[HT] [IPut]') == -1 and msg.find('[HT] [IGet]') == -1:
            continue

        mem_info = {}
        for field in msg[12:].split(', '):
            [key, value] = field.split('=')
            try:
                value_stored = int(value)
            except:
                value_stored = value
            mem_info[key] = value_stored

        __insert_or_append(pid_tid_mem, (pid, tid), mem_info)

    return pid_tid_mem


def heap_csv(in_path, out_path, pid, fields=None):
    if fields is None:
        fields = ['tshres', 'bytes_allocated', 'bytes_tl_bulk_allocated', 'heap_num_bytes_allocated']
    __csv_gen(in_path, out_path, pid, fields, __heap_processor)


def gc_csv(in_path, out_path, pid, fields=None):
    if fields is None:
        fields = ['tshres', 'gc_obj_freed', 'gc_bytes_freed', 'heap_obj_freed_ever', 'heap_bytes_freed_ever', 'heap_obj_allocated', 'heap_bytes_allocated']
    __csv_gen(in_path, out_path, pid, fields, __gc_processor)


def mem_csv(in_path, out_path, pid, fields=None):
    if fields is None:
        fields = ['tshres', 'method', 'field', 'iget', 'iput']
    __csv_gen(in_path, out_path, (pid, pid), fields, __mem_processor)
