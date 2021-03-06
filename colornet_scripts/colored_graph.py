from __future__ import print_function,division
import networkx as nx
import os,json
from sys import exit
from collections import Counter,defaultdict

script_path = os.path.dirname(os.path.realpath(__file__))
from sys import argv
get_item = lambda ind : lambda x: x[ind]


class ColoredGraph(object):

    def __init__(self,autoload=True,lonlatids=True):
        self.G = nx.Graph()
        self.color={}
        self.all_colors=set()
        self.lcbardict={}
        self.lcolor=set()
        self.seb_lcolor=[]
        self.lonlatids=lonlatids
        self.lonlat={}
        self.color_pair_dict = defaultdict(dict)
        if autoload:
            self.load_vertex_properties()
            self.load_edges()


    def load_edges(self,fname=None):
        fname =  os.path.join(script_path, "../real_data/caide-latest-complete-direct-edge-list.txt") if fname is None else fname
        with open(fname) as f:
            f.readline()
            for row in f:
                try:
                    i,j = row.strip().split()
                    self.G.add_edge(self.lonlat[int(i)],self.lonlat[int(j)])if self.lonlatids else self.G.add_edge(int(i),int(j))
                except ValueError:
                    pass

    def load_vertex_properties(self, fname=None):
        fname =  os.path.join(script_path, "../real_data/caide-latest-complete-direct-vertex-properties.txt") if fname is None else fname
        with open(fname) as f:
            f.readline();f.readline();f.readline()
            for row in f:
                thisid, thislat, thislon, thiscid, thisccode, thislcolor, thiskcore \
                        = row.strip().split()
                nodeid = (thislon,thislat) if self.lonlatids else int(thisid)
                self.color[nodeid] = thisccode
                self.lonlat[int(thisid)] = (thislon,thislat)
                self.all_colors.add(thisccode)
                if thislcolor == "1":
                    self.seb_lcolor.append(nodeid)
    def calculate_lcbar(self,to_avoid):
        all_seen=defaultdict(lambda : -1) #not visited nodes evaluate to -1
        double_counted=defaultdict(list)
        for source in self.G.nodes_iter(): #find all components from all sources
            if self.color[source] == to_avoid or source in all_seen:
            #don't start a search on a bad node
                continue
            seen={}                  # level (number of hops) when seen in BFS
            level=0                  # the current level
            nextlevel={source:1}  # dict of nodes to check at next level
            while nextlevel:
                thislevel=nextlevel  # advance to next level
                nextlevel={}         # and start a new list (fringe)
                for v in thislevel:
                    if v not in seen:
                        seen[v]=level
                        if all_seen[v] != -1: #this should only occur for a to_avoid node that was already counted
                            double_counted[all_seen[v]].append(v) # remember that this node also belongs to another tally
                        all_seen[v] = source
                        if self.color[v] != to_avoid:
                            nextlevel.update(self.G[v]) # add neighbors of v
                level=level+1
        comp_counter = Counter(all_seen.values())
        for key,doubles in double_counted.items():
            comp_counter[key]+=len(doubles)
        max_key,count = list(sorted(comp_counter.items(),key=get_item(1),reverse=True))[0]
        #print(max_key)
        lcbar = [node for node in self.G.nodes_iter() if all_seen[node] == max_key] + double_counted[max_key]
        self.lcbardict[to_avoid] = lcbar
        self.lcolor = self.lcolor.intersection(lcbar)
    def calculate_lcolor(self):
        self.lcolor = set(self.G.nodes_iter())
        for color in self.all_colors:
            self.calculate_lcbar(color)
    def calculate_color_sets(self):
        self.color_set = defaultdict(set)
        for v,color in self.color.items():
            self.color_set[color].add(v)
    def color_pair_connectivity(self,scolor,tcolor):
        connectible_nodes = set(self.G.nodes_iter())
        for color in filter(lambda x: x != scolor and x != tcolor, self.all_colors):
            connectible_nodes.intersection_update(self.lcbardict[color])
        self.color_pair_dict[scolor][tcolor] = len(self.color_set[scolor].intersection(connectible_nodes)) / len(self.color_set[scolor])
        self.color_pair_dict[tcolor][scolor] = len(self.color_set[tcolor].intersection(connectible_nodes)) / len(self.color_set[tcolor])
    def calculate_color_adjacency(self):
        self.calculate_color_sets()
        colors_list = sorted(self.all_colors,key=lambda x: len(self.color_set[x]),reverse=True)
        for i_1,scolor in enumerate(colors_list):
            print("%i %s"%(i_1,scolor))
            for tcolor in colors_list[i_1:]:
                self.color_pair_connectivity(scolor,tcolor)


    def set_networkx_attributes(self):
         two2three = json.load(open( os.path.join(script_path, "../real_data/iso2to3.json")))
         if self.lonlatids:
             nx.set_node_attributes(self.G,"lcolor",dict((k,1) if k in self.seb_lcolor else (k,0) for k in self.G.nodes_iter()))
         else:
             nx.set_node_attributes(self.G,"lcolor",dict((k,1) if k in self.lcolor else (k,0) for k in self.G.nodes_iter()))
         nx.set_node_attributes(self.G,"color",dict((k,bytes(two2three[v])) for k,v in self.color.items()))

