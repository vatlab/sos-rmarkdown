#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import argparse
import os
import re
import sys
import tempfile
import yaml

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from sos.utils import env
from sos_notebook.converter import execute_sos_notebook, notebook_to_html


def get_Rmarkdown_to_notebook_parser():
    parser = argparse.ArgumentParser(
        'sos convert FILE.Rmd FILE.ipynb (or --to ipynb)',
        description='''Export a Rmarkdown file kernel to a SoS notebook. It currently
        only handles code block and Markdown, and not inline expression.''')
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the converted notebook using sos-papermill')
    return parser


def Rmarkdown_to_notebook(rmarkdown_file,
                          output_file,
                          sargs=None,
                          unknown_args=None):
    cells = []
    code_count = 1

    #
    try:
        with open(rmarkdown_file) as script:
            rmdlines = script.readlines()
    except UnicodeDecodeError:
        env.logger.warning(f'Ignoring non-UTF8 characters from input Rmd file.')
        with open(rmarkdown_file, errors='ignore') as script:
            rmdlines = script.readlines()

    def add_cell(cells, content, cell_type, metainfo):
        nonlocal code_count
        # if a section consist of all report, report it as a markdown cell
        if not content:
            return
        if cell_type not in ('code', 'markdown'):
            env.logger.warning(
                f'Unrecognized cell type {cell_type}, code assumed.')
        #
        if cell_type == 'code':
            cells.append(
                new_code_cell(
                    # remove any trailing blank lines...
                    source=''.join(content).strip(),
                    execution_count=code_count,
                    metadata=metainfo))
            code_count += 1
        elif metainfo.get('kernel', '') == 'Markdown':
            # markdown code with inline expression
            cells.append(
                new_code_cell(
                    # remove any trailing blank lines...
                    source=f'%expand `r ` --in R\n' + ''.join(content).strip(),
                    execution_count=code_count,
                    metadata=metainfo))
            code_count += 1
        else:
            cells.append(
                new_markdown_cell(
                    source=''.join(content).strip(), metadata=metainfo))

    used_kernels = [['SoS', 'sos', '', '']]
    Rmd_header = {}
    # YAML front matter appears to be restricted to strictly ---\nYAML\n---
    re_yaml_delim = re.compile(r"^---\s*$")
    delim_lines = [i for i, l in enumerate(rmdlines) if re_yaml_delim.match(l)]
    if len(delim_lines) >= 2 and delim_lines[1] - delim_lines[0] > 1:
        yamltext = '\n'.join(rmdlines[delim_lines[0] + 1:delim_lines[1]])
        try:
            Rmd_header = yaml.safe_load(yamltext)
        except yaml.YAMLError as e:
            env.logger.warning(f"Error reading document metadata block: {e}")
            env.logger.warning("Trying to continue without header")
        rmdlines = rmdlines[:delim_lines[0]] + rmdlines[delim_lines[1] + 1:]

    lan_kernel_map = {
        'python': ['Python3', 'ir', '', ''],
        'sas': ['SAS', 'sas', '', ''],
        'ruby': ['Ruby', 'ruby', '', ''],
        'sh': ['Bash', 'bash', '', ''],
        'bash': ['Bash', 'bash', '', ''],
        'Node': ['JavaScript', 'javascript', '', ''],
        'r': ['R', 'ir', '', ''],
        'Rscript': ['R', 'ir', '', ''],
        'stata': ['Stata', 'stata', '', ''],
        'octave': ['Octave', 'octave', '', '']
    }

    re_code_start = re.compile(
        r'''
        ^````*\s*                        # ```
        {                                # {
        (?P<engine_name>                 # eignine name
        [a-zA-Z0-9]+                     # r
        )                                # end of engine name
        (\s+                             # space
        (?P<engine_options>.*)           #
        )?                               # options
        }                                # }
        \s*$                             #
        ''', re.VERBOSE)

    re_engine_option = re.compile(
        r'''
        engine\s*=\s*                    # engine =
        ["']
        (?P<engine_option>               # option
        [a-zA-Z0-9"']+
        )
        ["']
        ''', re.VERBOSE)

    re_code_end = re.compile(r"^````*\s*$")
    re_code_inline = re.compile(r"`r.+`")
    re_md_header = re.compile(r"^#+\s+")
    re_md_major_header = re.compile(r"^#{1,2}\s+")

    MD, CODE = range(2)

    state = MD
    celldata = []
    meta = {}
    has_inline_markdown = False

    for l in rmdlines:
        if state == MD:
            match = re_code_start.match(l)
            if match:
                state = CODE
                # only add MD cells with non-whitespace content
                if any([c.strip() for c in celldata]):
                    add_cell(cells, celldata, 'markdown', metainfo=meta)

                celldata = []

                engine_name = match.group('engine_name')
                chunk_opts = ''

                if match.group('engine_options'):
                    chunk_opts = match.group('engine_options').strip(" ,")
                    if chunk_opts:
                        meta['Rmd_chunk_options'] = chunk_opts

                    en_option = re_engine_option.search(
                        match.group('engine_options'))
                    if en_option and en_option.group('engine_option'):
                        engine_name = en_option.group('engine_option')

                if engine_name in lan_kernel_map:
                    meta['kernel'] = lan_kernel_map[engine_name][0]
                    if lan_kernel_map[engine_name] not in used_kernels:
                        used_kernels.append(lan_kernel_map[engine_name])
                else:
                    meta['kernel'] = engine_name
                    kinfo = [engine_name, engine_name, '', '']
                    if kinfo not in used_kernels:
                        used_kernels.append(kinfo)

                # show hide input/output
                if 'echo=FALSE' in chunk_opts and 'include=FALSE' not in chunk_opts:
                    # show only output
                    meta["jupyter"] = {
                        "source_hidden": True,
                        'output_hidden': False
                    }
                    meta['tags'] = ['report_output']
                elif 'include=FALSE' in chunk_opts:
                    # hide the entire cell
                    meta["jupyter"] = {
                        "output_hidden": True,
                        'source_hidden': True
                    }
                    meta['tags'] = ['scratch']
                elif 'echo=FALSE' not in chunk_opts:
                    # show input and output
                    meta["tags"] = ['report_cell']
                else:
                    # show only input
                    meta["jupyter"] = {"output_hidden": True}
            else:
                if re_code_inline.search(l):
                    if not meta.get('kernel', '') and any(
                            c.strip() for c in celldata):
                        # if there is markdown text before it, see if there are entire paragraphs
                        # and put in regular markdown cell
                        last_empty_line = len(celldata) - 1
                        while last_empty_line > 0:
                            if celldata[last_empty_line].strip():
                                last_empty_line -= 1
                            else:
                                break
                        if last_empty_line > 0 or re_md_header.match(
                                celldata[-1]):
                            add_cell(
                                cells,
                                celldata[:last_empty_line + 1],
                                'markdown',
                                metainfo=meta)
                            celldata = celldata[last_empty_line + 1:]
                            meta = {}
                    # inline markdown ...
                    has_inline_markdown = True
                    # we use hidden to indicate that the input of this code
                    # is supposed to be hidden
                    meta = {
                        'kernel': 'Markdown',
                        'jupyter': {
                            "source_hidden": True
                        },
                        'tags': ['report_output']
                    }
                # if we see a header, start a new cell
                if (re_md_header.match(l) and any(c.strip() for c in celldata)
                   ) or (celldata and re_md_major_header.match(celldata[-1])):
                    add_cell(cells, celldata, 'markdown', metainfo=meta)
                    celldata = []
                    meta = {}
                # cell.source in ipynb does not include implicit newlines
                celldata.append(l.rstrip() + "\n")
        else:  # CODE
            if re_code_end.match(l):
                state = MD
                # unconditionally add code blocks regardless of content
                add_cell(cells, celldata, 'code', metainfo=meta)
                celldata = []
                meta = {}
            else:
                if len(celldata) > 0:
                    celldata[-1] = celldata[-1] + "\n"
                celldata.append(l.rstrip())

    if state == CODE and any([c.strip() for c in celldata]):
        add_cell(cells, celldata, 'code', metainfo=meta)
    elif any([c.strip() for c in celldata]):
        add_cell(cells, celldata, 'markdown', metainfo=meta)
    #
    # create header
    metadata = {
        'kernelspec': {
            "display_name": "SoS",
            "language": "sos",
            "name": "sos"
        },
        "language_info": {
            "file_extension": ".sos",
            "mimetype": "text/x-sos",
            "name": "sos",
            "pygments_lexer": "python",
            'nbconvert_exporter': 'sos_notebook.converter.SoS_Exporter',
        },
        'sos': {
            'kernels': used_kernels
        }
    }
    if has_inline_markdown:
        metadata['sos']['kernels'].append(['Markdown', 'markdown', '', ''])
    if Rmd_header:
        metadata['Rmd_chunk_options'] = Rmd_header

    nb = new_notebook(cells=cells, metadata=metadata)

    if sargs.execute:
        if output_file:
            execute_sos_notebook(nb, output_file)
            env.logger.info(f'Jupyter notebook saved to {output_file}')
            return
        else:
            nb = execute_sos_notebook(nb)

    if not output_file:
        nbformat.write(nb, sys.stdout, 4)
    else:
        with open(output_file, 'w') as new_nb:
            nbformat.write(nb, new_nb, 4)
        env.logger.info(f'Jupyter notebook saved to {output_file}')


def get_Rmarkdown_to_html_parser():
    parser = argparse.ArgumentParser(
        'sos convert FILE.Rmd FILE.html (or --to ipynb)',
        description='''Export a Rmarkdown file kernel to a SoS report. It currently
        only handles code block and Markdown, and not inline expression.''')
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the notebook using sos-papermill before exporting a report in HTML format.'
    )
    parser.add_argument(
        '--template',
        help='''Template to export Jupyter notebook with sos kernel. SoS provides a number
        of templates, with sos-report displays markdown cells and only output of cells with
        prominent tag, and a control panel to control the display of the rest of the content
        ''')
    parser.add_argument(
        '-v',
        '--view',
        action='store_true',
        help='''Open the output file in a broswer. In case no html file is specified,
        this option will display the HTML file in a browser, instead of writing its
        content to standard output.''')
    return parser


def Rmarkdown_to_html(rmarkdown_file,
                      output_file,
                      sargs=None,
                      unknown_args=None):
    notebook_file = tempfile.NamedTemporaryFile(
        prefix='__output_nb', dir=os.getcwd(), suffix='.ipynb',
        delete=False).name
    Rmarkdown_to_notebook(
        rmarkdown_file, notebook_file, sargs=sargs, unknown_args=unknown_args)
    # if --execute is specified, it must have been execute during Rmarkdown_to_notebook
    sargs.execute = False
    #
    try:
        notebook_to_html(notebook_file, output_file, sargs, unknown_args)
    finally:
        try:
            os.remove(notebook_file)
        except Exception as e:
            env.logger.warning(
                f'Failed to remove temporary output file {notebook_file}: {e}')
