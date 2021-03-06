#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Sat Nov 28 15:45:43 2015

@author: jeff

This script aggregates information from multiple '.edge_data.csv' files
produces by running paprica on multiple samples.  It produces a matrix of edges
by sample, and a matrix of mean edge parameters, by sample.

Run as: python combine_edge_results.py -edge_in [suffix pattern for edges] -path_in [suffix pattern for paths] -ec_in [suffix pattern for ec numbers] -unique_in [suffix pattern for unique sequences] -o [prefix for output]

It will automatically loop through all files in the directory with the specified suffixes.

"""

import os
import pandas as pd
import re
import math
import sys

## Read in command line arguments.

command_args = {}

for i,arg in enumerate(sys.argv):
    if arg.startswith('-'):
        arg = arg.strip('-')
        try:
            command_args[arg] = sys.argv[i + 1]
        except IndexError:
            command_args[arg] = ''
        
if 'h' in command_args.keys():
    pass
    #print help_string ## no help sting
    quit()

try:
    prefix = command_args['o']
except KeyError:
    prefix = 'combined_results'

try:
    edge_suffix = command_args['edge_in']
except KeyError:
    edge_suffix = 'eukarya.edge_data.csv'
    
try:
    path_suffix = command_args['path_in']
except KeyError:
    path_suffix = 'eukarya.sum_pathways.csv'
    
try:
    ec_suffix = command_args['ec_in']
except KeyError:
    ec_suffix = 'eukarya.sum_ec.csv'
    
try:
    unique_suffix = command_args['unique_in']
except KeyError:
    unique_suffix = False
    
def stop_here():
    stop = []
    print 'Manually stopped!'
    print stop[1]

edge_tally = pd.DataFrame()
edge_data = pd.DataFrame()
ec_tally = pd.DataFrame()
path_tally = pd.DataFrame()

def fill_edge_data(param, name, df_in):
    temp = []
    for index in df_in.index:
        
        ## Exception is necessary for old version of build_core_genomes which
        ## did not provide a n16S value for draft genomes.
        
        try:
            n = range(int(math.ceil(df_in.loc[index, 'nedge_corrected'])))
        except ValueError:
            n = range(int(df_in.loc[index, 'nedge']))
            
        for i in n:
            temp.append(df_in.loc[index, param])
            
    temp = pd.Series(temp)
            
    mean = temp.mean()
    sd = temp.std()
    
    print name, param, mean, sd
    return mean, sd
        
for f in os.listdir('.'):
    if f.endswith(edge_suffix):
        
        temp_edge = pd.read_csv(f, index_col = 0)
        name = re.sub(edge_suffix, '', f)
        
        for param in ['n16S', 'nge', 'ncds', 'genome_size', 'GC', 'phi', 'confidence']:
            edge_data.loc[name, param + '.mean'], edge_data.loc[name, param + '.sd'] = fill_edge_data(param, name, temp_edge)
        
        if len(pd.isnull(pd.DataFrame(temp_edge['nedge_corrected'])) > 0):
            temp_edge_abund = pd.DataFrame(temp_edge['nedge'])
        else:
            temp_edge_abund = pd.DataFrame(temp_edge['nedge_corrected'])
            
        temp_edge_abund.columns = [name]        
        edge_tally = pd.concat([edge_tally, temp_edge_abund], axis = 1)
            
    elif f.endswith(path_suffix):
        name = re.sub(path_suffix, '', f)
        temp_path = pd.read_csv(f, index_col = 0, names = [name])
        path_tally = pd.concat([path_tally, temp_path], axis = 1)
        
    elif f.endswith(ec_suffix):
        name = re.sub(ec_suffix, '', f)
        temp_ec = pd.read_csv(f, index_col = 0, names = [name])
        ec_tally = pd.concat([ec_tally, temp_ec], axis = 1)
            
pd.DataFrame.to_csv(edge_tally.transpose(), prefix + '.edge_tally.csv')
pd.DataFrame.to_csv(edge_data.transpose(), prefix + '.edge_data.csv') 
pd.DataFrame.to_csv(path_tally.transpose(), prefix + '.path_tally.csv') 
pd.DataFrame.to_csv(ec_tally.transpose(), prefix + '.ec_tally.csv')

if unique_suffix != False:
    unique_tally = pd.DataFrame()
    
    for f in os.listdir('.'):
        if f.endswith(unique_suffix):
            name = re.sub(unique_suffix, '', f)
            temp_unique = pd.read_csv(f, index_col = 0, usecols = ['identifier', 'abundance_corrected'])
            temp_unique.columns = [name]
            unique_tally = pd.concat([unique_tally, temp_unique], axis = 1)
        
    pd.DataFrame.to_csv(unique_tally, prefix + '.unique_tally.csv')        