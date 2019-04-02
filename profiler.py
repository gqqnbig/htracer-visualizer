#! /usr/bin/env python3
# /usr/bin/evn is a program, it searches the location of python3 and calls it.

import sys

import log_processer as lg

import dash
import dash_core_components as dcc
import dash_html_components as dhc
import pandas as pd


if __name__ == '__main__':
    # log_path = './logs/mar19-1/trace-chrome-1'
    # pid = xxxx

    log_path = sys.argv[1]
    pid = int(sys.argv[2])

    lg.clean(log_path, log_path+'-clean')
    lg.heap_filter(log_path+'-clean', log_path+'-heap')
    lg.gc_filter(log_path+'-clean', log_path+'-gc')
    lg.sys_gc_filter(log_path+'-clean', log_path+'-sysgc')
    lg.mem_filter(log_path+'-clean', log_path+'-mem')

    lg.heap_csv(log_path + '-heap', log_path + f'-{pid}-heap.csv', pid)
    lg.gc_csv(log_path + '-gc', log_path + f'-{pid}-gc.csv', pid)
    lg.mem_csv(log_path + '-mem', log_path + f'-{pid}-mem.csv', pid)

    heap_csv = pd.read_csv(log_path + f'-{pid}-heap.csv')
    heap_tshres = heap_csv.tshres
    heap_heap_num_bytes_allocated = heap_csv.heap_num_bytes_allocated

    gc_csv = pd.read_csv(log_path + f'-{pid}-gc.csv')
    gc_tshres = gc_csv.tshres
    gc_gc_bytes_freed = gc_csv.gc_bytes_freed

    mem_csv = pd.read_csv(log_path + f'-{pid}-mem.csv')
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
