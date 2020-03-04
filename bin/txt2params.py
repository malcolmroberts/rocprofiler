#!/usr/bin/python

################################################################################
# Copyright (c) 2018 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################

import os, sys, re

def gen_params(txtfile):
  fields = {} 
  parent_field = ''
  nbr_indent = 0
  nbr_indent_prev = 0
  check_for_dims = False
  with open(txtfile) as fp: 
    for line in fp: 
      mv = re.match(r'HCC clang version\s+(.*)',line)
      if mv:
        key = 'HCCclangversion'
        val = mv.group(1)
        fields[key] = val
        continue
      if check_for_dims == True:
        mc = re.match(r'\s*([x|y|z])\s+(.*)',line) 
        if mc:
          key_sav = mc.group(1)
          if parent_field != '':
            key = parent_field + '_' + mc.group(1)
          else:
            key = mc.group(1)
          val = re.sub(r"\s+", "", mc.group(2))
          fields[key] = val
          if key_sav == 'z':
            check_for_dims = False
      nbr_indent_prev = nbr_indent
      mi = re.search(r'^(\s+)\w+', line)
      md = re.search(':', line)
      if mi:
        nbr_indent = len(mi.group(1)) / 2 #indentation cnt
      else:
        if not md:
          tmp = re.sub(r"\s+", "", line)
          if tmp.isalnum():
            parent_field = tmp
            continue

      if nbr_indent < nbr_indent_prev:
        pos = parent_field.rfind('_')
        if pos != -1:
          parent_field = parent_field[:pos] # remove last _*

      for lin in line.split(';'):
        lin = re.sub(r"\s+", "", lin)
        m = re.match(r'(.*):(.*)', lin)
        if m:
          key, val = m.group(1), m.group(2)
          if parent_field != '':
            key = parent_field + '_' + key
          if val == '':
            mk = re.match(r'.*Dimension',key)
            if mk: # expect x,y,z on next 3 lines
               check_for_dims = True
            parent_field = key 
          else:
            fields[key] = val
        else:
          if nbr_indent != nbr_indent_prev and not check_for_dims :
            parent_field = parent_field + '_' + lin.replace(':','')

  return fields 
