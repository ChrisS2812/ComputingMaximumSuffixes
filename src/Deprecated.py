# #Helping function that computes all paths below a given index
# def compute_paths_below_index(index):
#     if is_leaf(index) or is_last_comp(index):
#         return []
#     else:
#         leftmost_child_index = index
#         rightmost_child_index = index
#         #get left- and rightmost (grand-)child
#         while not is_last_comp(leftmost_child_index):
#             leftmost_child_index = leftmost_child_index*3 + 1
#             rightmost_child_index = rightmost_child_index*3 + 3
        
#         result = []
#         for i in range(leftmost_child_index, rightmost_child_index+1):
#             current_path = []
#             current_index = i
#             while(current_index != index):
#                 current_path.insert(0, current_index)
#                 current_index = (current_index-1) // 3
#             result.append(current_path)
#         return result


# #Helping function that computes all paths through a given index
# def compute_paths_through_index(index):
#     if is_leaf(index):
#         index = (index - 1) // 3
        
#     path_to_index = []
#     index_buffer = index
#     while index_buffer != 0:
#         path_to_index.insert(0, index_buffer)
#         index_buffer = (index_buffer - 1) // 3
#     path_to_index.insert(0,0)

#     if is_last_comp(index):
#         return [path_to_index]
#     result = []
#     for path in compute_paths_below_index(index):
#         result.append(path_to_index + path)
#     return result


# #Helping function that returns all indices contained in the subtree with root at given index
#def get_subtree_indices(index):
#     result = [index]
#     if is_leaf(index):
#         return []
#     elif is_last_comp(index):
#         return result
#     else:
#         result.extend(get_children(index*3 + 1))
#         result.extend(get_children(index*3 + 2))
#         result.extend(get_children(index*3 + 3))
#         return result


##Create a dict that saves all "blacklist paths" i.e. paths that have been found to not be allowed to be contained in any tree because we have found two words that ##follow this same path but have another r-value.
##It maps from a (unique) string representation of a blacklist path to the actual path in list form: 
##string -> (c_1, r_1, c_2, r_2, ..., c_M, r_M) where c_i represents a comparison and r_i the result of this comparison ("<", "=", or ">")
# blacklist_dict = {}

# #insert all possible keys with value False in dict
# comp_perms = list(itertools.permutations(comp_pairs, M))
# res_perms = list(itertools.product(["<","=",">"], repeat=M))

# for cp in comp_perms:
#     for rp in res_perms:
#         bl_key = ''
#         for i in range(M):
#             bl_key += str(cp[i])
#             if i != M-1:
#                 bl_key += rp[i]
#         blacklist_dict[bl_key] = 0

# #Helping function that decides whether a node at a certain index is blocked, i.e. whatever its value is, its path is contained in the blacklist
# def is_blocked(alg, index):
#     actual_comp = alg[index].obj #must be reset to the correct value in the end

#     for comp in comp_pairs:
#         alg[index].obj = comp
#         path_repr = compute_path_repr_for_index(alg, index)
#         for pr in path_repr:
#             #Case 1: Legal path found
#             if (pr in blacklist_dict and blacklist_dict[pr] == 0):
#                 alg[index].obj = actual_comp
#                 return False
#     #Case 3: All possible paths are illegal
#     alg[index].obj = actual_comp
#     return True

# #Helping function that decides whether all paths going through a node are legal, i.e. do not contain a comparison twice and are not blacklisted
# def is_legal(alg, index):
#     for path in compute_paths_through_index(index):
#         comps = set(list(map(lambda i: alg[i].obj, path)))
#         if len(comps) < M:
#             return False
        
#     path_repr = compute_path_repr_for_index(alg, index)
    
#     for rep in path_repr:
#         if blacklist_dict[rep] == 1:
#             return False
#     return True



#                         if not is_rightmost:
#                             #Not rightmost child: Just search for first comparison that fulfils Rule 1, 
#                             #i.e. that has not yet been executed on this path 
#                             #(Rule 2 will be fulfilled by rightmost node)
#                             alg.append(Node(current_index, obj=pair, parent=parent))
#                             current_index += 1
#                             break
#                         elif (pair not in parent_values) and (pair != alg[current_index-1].obj 
#                                                                 or pair != alg[current_index-2].obj):
#                             #Rightmost child: must find a value that also fulfils Rule 2 i.e. defines a 
#                             #different "state" for the parent node
#                             alg.append(Node(current_index, obj=pair, parent=parent))
#                             current_index += 1
#                             break


# #Computes the next algorithm that has a chance of being correct. The parameters are:
# #* index: indicates the index of the node whose comparison was found to be false, i.e. its value should be increased
# #* curr_alg: represents the current decision tree that will be manipulated by this method
# def generate_next_algorithm(index, curr_alg):
#     increase_index = index
#     check_legal_set = set()
    
#     while True:
#         if increase_index == 0:
#             root_obj = curr_alg[increase_index].obj
#             #Check if we are trying to increase a root that has already the last possible comparison -> Finished
#             if root_obj == comp_pairs[-1]:
#                 print("Finished!")
#                 #saving final tree
#                 DotExporter(curr_alg[0], nodeattrfunc=lambda node: 'label="{}"'.format(node.obj)).to_picture("{}/final_graph.png".format(dir))
#                 return -42
#             else:
#                 current_root_index = comp_pairs.index(root_obj)
#                 next_root_value = comp_pairs[current_root_index + 1]
#                 if DEBUG:
#                     print("[Increasing] Setting value of node at index 0 from {} to {}".format(root_obj, next_root_value))
#                 return generate_algorithm(next_root_value)

#         current_node = curr_alg[increase_index]
#         current_node_comp = current_node.obj

#         #(1) Compute comparisons on path to current index
#         comps_on_current_path = [current_node_comp] 
#         index_buffer = increase_index
#         while index_buffer != 0:
#             index_buffer = (index_buffer-1)//3
#             comps_on_current_path.append(alg[index_buffer].obj)

#         #(2) Find new comparison value that fulfils Rule 1+2
#         next_comp_index = comp_pairs.index(current_node_comp) #init

#         invalid_found = False
#         while(True):
#             next_comp_index += 1
#             if next_comp_index == len(comp_pairs):
#                 #could not find any higher value for this node - try it with next bigger node
#                 if DEBUG and (not(ONLY_HIGHEST_DEBUG) or increase_index < 5):
#                     print("[Rule 1] Did not find any higher value for node at index {}. Continuing at {}".format(increase_index, increase_index-1))
#                 increase_index = increase_index - 1
#                 invalid_found = True
#                 break

#             next_comp = comp_pairs[next_comp_index]

#             if next_comp not in comps_on_current_path:
#                 #Rule 1 fulfilled
#                 if increase_index %3 != 0 or curr_alg[index-1].obj != next_comp or curr_alg[increase_index-2].obj != next_comp:
#                     #either not rightmost child or at least another sibling with another value -> rule 2 fulfilled
#                     previous_comp = curr_alg[increase_index].obj
#                     curr_alg[increase_index].obj = next_comp
#                     check_legal_set.add(increase_index)
#                     if DEBUG and (not(ONLY_HIGHEST_DEBUG) or increase_index < 5):
#                         print("[Increasing] Setting value of node at index {} from {} to {}".format(increase_index, previous_comp, next_comp))
#                     break
                    
#         if invalid_found:
#             continue


#         #(3) Rule 3: Every height value must have at least two different states
#         # skipped for now, bc. assumed: Rule 2 + choice of minimal values for each node => Rule 3???

#         #(4) Postprocessing: All nodes on the right of the increased node must be decreased as far as possible
#         #in order to not skip any possibly correct algorithm.
#         for decrease_index in range(increase_index+1, len(curr_alg)):
#             if is_leaf(decrease_index):
#                 break
#             current_node = curr_alg[decrease_index]

#             #build up list of disallowed values
#             node_buffer = curr_alg[decrease_index]
#             current_comp = node_buffer.obj
#             current_blacklist = []
#             while(node_buffer.parent != None):
#                 node_buffer = node_buffer.parent
#                 current_blacklist.append(node_buffer.obj)
#             if decrease_index % 3 == 0 and (curr_alg[decrease_index-1].obj == (curr_alg[decrease_index-2].obj)):
#                 siblings_value = curr_alg[decrease_index-1].obj
#                 if siblings_value not in current_blacklist:
#                     #right node: must not be the same as the other two children if they are equal
#                     rule_2_value = curr_alg[decrease_index-1].obj
#                     current_blacklist.append(rule_2_value)
            
#             allowed_comps = [c for c in comp_pairs if c not in current_blacklist]
#             for allowed_comp in allowed_comps:
#                 previous_comp = current_node.obj
#                 current_node.obj = allowed_comps[0]
#                 if previous_comp != allowed_comps[0]:
#                     check_legal_set.add(decrease_index)
#                 if DEBUG and current_node.obj != previous_comp and (not(ONLY_HIGHEST_DEBUG) or decrease_index < 5):
#                     print("[Decreasing] Setting value of node at index {} from {} to {}".format(decrease_index, previous_comp, allowed_comps[0]))
#                 break
        
#         invalid_found = False
#         check_legal_list = list(check_legal_set)
#         check_legal_list.sort(reverse=True)
#         checked_set = set()
#         for check_index in check_legal_list:
#             checked_set.add(check_index)
#             if is_blocked(curr_alg, check_index):
#                 if DEBUG and (not(ONLY_HIGHEST_DEBUG) or decrease_index < 5):
#                     print("[Blacklist] Blocked path found at index {} - continuing at {}".format(check_index, (check_index - 1) // 3))
#                 increase_index = (check_index - 1) // 3
#                 invalid_found = True
#                 break
#         for checked in checked_set:
#             check_legal_set.remove(checked) 
#         if invalid_found:
#             continue
#         if not check_legal_set:
#             return curr_alg

# Helping function that computes (all) decision-tree-independent path representation on which a given index lies.
# A path is a string of the form:
# * c_1r_1c_2_r_2...c_M
# where c_i represents a comparison and r_i the result of this comparison ("<", "=", or ">")
# def compute_path_repr_for_index(self, alg, index):
#     if self.is_leaf(index=index):
#         return self.compute_path_repr_for_index(alg, (index - 1) // 3)
#     if self.is_last_comp(index=index):
#         # start at lowest comparison node (the last node is not important for blacklisted paths)
#         re = str(alg[index].obj)
#         while index != 0:
#             mod = index % 3
#             if mod == 0:
#                 re = ">" + re
#             elif mod == 1:
#                 re = "<" + re
#             else:
#                 re = "=" + re
#             index = (index - 1) // 3
#             re = str(alg[index].obj) + re
#         return [re]
#     else:
#         result = []
#         # Append paths for all children
#         result.extend(self.compute_path_repr_for_index(alg, index * 3 + 1))
#         result.extend(self.compute_path_repr_for_index(alg, index * 3 + 2))
#         result.extend(self.compute_path_repr_for_index(alg, index * 3 + 3))
#         return result

# # Helping function that decides whether a node at a given index represents the last comparison
# def is_last_comp(self, index):
#     if self.m < 1:
#         return False
#
#     if self.compute_depth(index) == self.m - 1:
#         return True
#     return False