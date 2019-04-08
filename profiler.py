#! /usr/bin/env python3
# /usr/bin/evn is a program, it searches the location of python3 and calls it.

import sys

import log_processer as lg

import dash
import dash_core_components as dcc
import dash_html_components as dhc
import pandas as pd

import os
import re

if __name__ == '__main__':
    # log_path = './logs/mar19-1/trace-chrome-1'
    # pid = xxxx

    pid = 0
    heapFileName = ''
    gcFileName = ''
    memFileName = ''

    argv=sys.argv[:]
    pruneFiles="--prune" in argv
    if pruneFiles:
        argv.remove("--prune")

    if len(argv) == 2:
        for file in os.listdir(argv[1]):
            if re.search("-\\d+-heap.csv$", file):
                heapFileName = os.path.join(argv[1], file)
            elif re.search("-\\d+-gc.csv$", file):
                gcFileName = os.path.join(argv[1], file)
            elif re.search("-\\d+-mem.csv$", file):
                memFileName = os.path.join(argv[1], file)
            elif pruneFiles:
                os.remove(os.path.join(argv[1], file))

        pid = re.search("-(\\d)+-heap.csv$", heapFileName).group(1)
    elif len(argv) == 3:
        log_path = argv[1]
        pid = int(argv[2])

        heapFileName = log_path + f'-{pid}-heap.csv'
        gcFileName = log_path + f'-{pid}-gc.csv'
        memFileName = log_path + f'-{pid}-mem.csv'

        lg.clean(log_path, log_path + '-clean')
        lg.heap_filter(log_path + '-clean', log_path + '-heap')
        lg.gc_filter(log_path + '-clean', log_path + '-gc')
        lg.sys_gc_filter(log_path + '-clean', log_path + '-sysgc')
        lg.mem_filter(log_path + '-clean', log_path + '-mem')

        lg.heap_csv(log_path + '-heap', heapFileName, pid)
        lg.gc_csv(log_path + '-gc', gcFileName, pid)
        lg.mem_csv(log_path + '-mem', memFileName, pid)
    else:
        print("Incorrect number of parameters.")
        print("profiler.py [--prune] folder")
        print("profiler.py trace-file pid")
        print("")
        print("--prune removes unnecessary files in the folder.")
        sys.exit(0)

    heap_csv = pd.read_csv(heapFileName)
    heap_tshres = heap_csv.tshres
    heap_heap_num_bytes_allocated = heap_csv.heap_num_bytes_allocated

    gc_csv = pd.read_csv(gcFileName)
    gc_tshres = gc_csv.tshres
    gc_gc_bytes_freed = gc_csv.gc_bytes_freed

    mem_csv = pd.read_csv(memFileName)
    mem_tshres = mem_csv.tshres
    mem_iget = mem_csv.iget
    mem_iput = mem_csv.iput

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = dhc.Div(children=[
        dhc.H1(children=f'Android Runtime Profiler'),
        dcc.Graph(
            id='heap-gc',
            figure={
                'data': [
                    {'x': heap_tshres, 'y': heap_heap_num_bytes_allocated, 'type': 'lines', 'name': 'heap size'},
                    {'x': gc_tshres, 'y': gc_gc_bytes_freed, 'type': 'bar', 'name': 'gc size'},
                ],
                'layout': {
                    'title': f'heap gc, pid={pid}',
                }
            }
        ),
        dcc.Graph(
            id='mem-read-write',
            figure={
                'data': [
                    {'x': mem_tshres, 'y': mem_iget, 'type': 'lines', 'name': 'read'},
                    {'x': mem_tshres, 'y': mem_iput, 'type': 'lines', 'name': 'write'},
                ],
                'layout': {
                    'title': f'memory access, pid={pid}',
                }
            }
        )
    ])
    app.run_server(debug=True)
