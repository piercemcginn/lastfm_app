import json
import requests
import pandas as pd
import numpy as np
from graphviz import Digraph, Graph

bros=['pierce345', 'dmcginn615', 'smcginn410', 'summerjets', 'iamdarrencheung']
# bros=['pierce345', 'summerjets']
methodlist=['topartists', 'recenttracks']
methods={'topartists':'user.getTopArtists', 'recenttracks': 'user.getrecenttracks'}
keywords={'topartists':'artist', 'recenttracks': 'track'}
url='http://ws.audioscrobbler.com/2.0/?api_key=19b52576c07c45c1fe0e813645cb30e1&format=json'

def grab(bro, method):
    '''returns the json retrieved from lastfm for user BRO and method METHOD and gives 1000 entries'''
    return json.loads(requests.get(url+'&user='+bro+'&method='+methods[method]+'&limit=1000').content)

def extract(bro, method, data, key):
    '''returns a list of information extracted from a passed json, DATA, corresponing to key KEY'''
    dummy=[]
    for i in range(len(data[bro][method][keywords[method]])):
        dummy.append(data[bro][method][keywords[method]][i][key])
    return dummy

def assemble(bro, method, info):
    ''''''
    data={}
    data[bro]=grab(bro, method)
    return extract(bro, method, data, info)

def similars(artist):
    ''''''
    data=json.loads(requests.get(url+'&method=artist.getsimilar'+'&artist='+artist+'&limit=1000').content)
    dummy=[]
    dummy2=[]
    for i in range(len(data['similarartists']['artist'])):
        dummy.append(data['similarartists']['artist'][i]['name'])
        dummy2.append(data['similarartists']['artist'][i]['match'])
    return pd.DataFrame({'Artist': dummy, 'Match': dummy2})

def collect_artists():
    data={}
    data2={}
    my_artists={}
    for bro in bros:
        data[bro]=assemble(bro, 'topartists', 'name')
        data2[bro]=assemble(bro, 'topartists', 'playcount')
        my_artists[bro]=pd.DataFrame({'Artist': data[bro], 'Playcount': data2[bro]})
        my_artists[bro]['Playcount']=my_artists[bro]['Playcount'].apply(lambda x: int(x))
    return my_artists

# my_artists=collect_artists()

def rec(bro, my_artists):
    my_similars={}
    my_similars_shared={}
    my_similars[bro]=pd.DataFrame({'Artist': [], 'Match': []})

    for artist in my_artists[bro][my_artists[bro]['Playcount']>50]['Artist']:
        try:
            my_similars[bro]=my_similars[bro].append(similars(artist)) #create list of all artists similar to user's artists
        except:
            pass

    # my_similars[bro]=my_similars[bro][my_similars[bro]['Match']>0.5]
    my_similars[bro]=my_similars[bro].sort_values(by=['Match'], ascending=False)
    my_similars[bro]=my_similars[bro].drop_duplicates(subset='Artist', keep='first')
    my_similars[bro]=my_similars[bro].merge(my_artists[bro]['Artist'], on="Artist", how='left', indicator=True)
    my_similars[bro]=my_similars[bro][my_similars[bro]['_merge']=='left_only'][['Artist', 'Match']]

    return my_similars[bro]

def bro_rec(bro, bro2, my_artists):
    my_similars={}
    my_similars_shared={}
    my_similars[bro]=pd.DataFrame({'Artist': [], 'Match': []})

    for artist in my_artists[bro][my_artists[bro]['Playcount']>20]['Artist']:
        try:
            my_similars[bro]=my_similars[bro].append(similars(artist)) #create list of all artists similar to user's artists
        except:
            pass

    # my_similars[bro]=my_similars[bro][my_similars[bro]['Match']>0.25]
    my_similars[bro]=my_similars[bro].sort_values(by=['Match'], ascending=False)
    my_similars[bro]=my_similars[bro].drop_duplicates(subset='Artist', keep='first')
    my_similars[bro]=my_similars[bro].merge(my_artists[bro]['Artist'], on="Artist", how='left', indicator=True)
    my_similars[bro]=my_similars[bro][my_similars[bro]['_merge']=='left_only'][['Artist', 'Match']]

    return my_similars[bro].merge(my_artists[bro2][my_artists[bro2]['Playcount']>10], on="Artist", how='inner')

def create_graph(subject, my_artists, total, minmatch):
    if total==0:   #if total is given as zero, do for all artists
        total=len(my_artists[subject]['Artist'])-1

    edges=[]

    for artist in my_artists[subject]['Artist'][:total]:   #for each of my artists
        try:
            sim=similars(artist)    #get a list of similar artists

            for artist2 in my_artists[subject]['Artist'][:total]: #only artists lower in list-prevents double entries
                if artist2 in sim['Artist'].tolist():             #if any of them are similar to the first
                    index=my_artists[subject].index[my_artists[subject]['Artist'] == artist][0] #index in original list
                    index2=my_artists[subject].index[my_artists[subject]['Artist'] == artist2][0]
                    match=float(sim.loc[sim['Artist'] == artist2, 'Match'])
                    if match>minmatch:
                        edges.append((artist, index, artist2, index2, match))
        except:
            pass
    return edges

def plot_graph(subject, my_artists, edges, total):
    dot = Digraph(comment='Music Cluster')
    i=0

    for artist in my_artists[subject]['Artist'][:total]:
        dot.node(str(i), artist)
        i+=1

    for edge in edges:
        dot.edge(str(edge[1]), str(edge[3]))

    dot.render('test-output/round-table.gv', view=True)
