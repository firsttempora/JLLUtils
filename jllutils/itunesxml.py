from __future__ import print_function
import datetime as dt
import re


def read_lib_file(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
        
    return ''.join([l.strip() for l in lines])

def parse_array(astr):
    aout = []
    for el, tag in iter_elements(astr):
        aout.append(parse_element(el, tag))
        
    return aout
        
def parse_dict(dstr):
    looking_for_key = True
    dout = dict()
    for el, tag in iter_elements(dstr):
        if looking_for_key:
            if tag != '<key>':
                raise ValueError('Did not find a key when I expected to')
            key = el
        else:
            val = parse_element(el, tag)
            dout[key] = val
            
        looking_for_key = not looking_for_key
        
    return dout
    
def parse_element(el, tag):
    if tag is None:
        return el
    elif tag == '<integer>':
        return int(el)
    elif tag == '<float>':
        return float(el)
    elif tag == '<string>' or tag == '<data>':
        return el
    elif tag == '<array>':
        return parse_array(el)
    elif tag == '<dict>':
        return parse_dict(el)
    elif tag == '<date>':
        return dt.datetime.strptime(el, '%Y-%m-%dT%H:%M:%SZ')
    else:
        raise NotImplementedError('Cannot parse element with tag {}'.format(tag))
    
def find_next_element(data):
    m = re.search('<.*?>', data)
    # iTunes lib XML seems to use <true/> and <false/> as single tag elements
    if re.match('<.*/>', m.group()):
        if m.group() == '<true/>':
            val = True
        elif m.group() == '<false/>':
            val = False
        else: 
            val = m.group()
        return val, None, m.end()
    else:
        # Otherwise we need to find the closing tag, which means accounting for nested elements of the same type
        tag = m.group()
        closing_tag = m.group().replace('<','</')
        reobj = re.compile('{}|{}'.format(tag, closing_tag))
        slice_start_ind = m.end()
        nest_level = 1
        n = m # just to give us a non-None match group
        ind = slice_start_ind
        while nest_level > 0 and n is not None:
            n = reobj.search(data, pos=ind)
            if n.group() == tag:
                nest_level += 1
            elif n.group() == closing_tag:
                nest_level -= 1
            else:
                raise NotImplementedError('Match does not equal opening or closing tag')
            ind = n.end()
            slice_end_ind = n.start()
            
        if nest_level > 0:
            raise RuntimeError('Did not close tag {} starting at character {}'.format(m.group()), m.start())
        
        return data[slice_start_ind:slice_end_ind], tag, ind
    
def iter_elements(data):
    ind = 0
    while ind < len(data):
        el, tag, nextind = find_next_element(data[ind:])
        yield el, tag
        ind += nextind
        
def parse_itunes_lib(lib_file):
    lib_str = read_lib_file(lib_file)
    sind = lib_str.index('<dict>')
    main_dict, tag, _ = find_next_element(lib_str[sind:])
    if tag != '<dict>':
        raise RuntimeError('Expecting to start with a dict')
    return parse_dict(main_dict)

# Yes the next two methods should really be done via OOP... I'm in a hurry
def track_in_list(t,l):
    for t2 in l:
        if are_tracks_eq(t,t2):
            return True
        
    return False
    
def are_tracks_eq(t1, t2):
    #test_keys = ['Album', 'Artist', 'Name', 'Size', 'Total Time', 'Year']
    test_keys = ['Album', 'Artist', 'Name', 'Year']
    for k in test_keys:
        if k in t1.keys() and k in t2.keys():
            if t1[k] != t2[k]:
                return False
        elif k in t1.keys() and k not in t2.keys():
            return False
        elif k not in t1.keys() and k in t2.keys():
            return False

    
    return True
    
def music_diff(d1, d2):
    in_d1_not_d2 = []
    in_d2_not_d1 = []
    for t in d1['Tracks'].values():
        if not track_in_list(t, d2['Tracks'].values()):
            in_d1_not_d2.append(t)
    for t in d2['Tracks'].values():
        if not track_in_list(t, d1['Tracks'].values()):
            in_d2_not_d1.append(t)
            
    return in_d1_not_d2, in_d2_not_d1
    
def assemble_playlist(plist, tracks):
    tracks_out = []
    if 'Playlist Items' not in plist.keys():
        return tracks_out
    for t in plist['Playlist Items']:
        k = str(t['Track ID'])
        tracks_out.append(tracks[k])
        
    return tracks_out
    
def match_playlists(plist, plists_to_match):
    matched = []
    for p in plists_to_match:
        if p['Name'] == plist['Name']:
            matched.append(p)
            
    return matched
    
def format_track(track):
    artist = track['Artist'] if 'Artist' in track.keys() else ''
    album = track['Album'] if 'Album' in track.keys() else ''
    year = track['Year'] if 'Year' in track.keys() else ''
    name = track['Name'] if 'Name' in track.keys() else ''
        
    return '{} in {} ({}): "{}"'.format(artist, album, year, name)
    
def assemble_report(old_lib_file, new_lib_file, log_file=None):  
    # First we need to parse the two files
    print('Parsing old lib file...')
    old_lib = parse_itunes_lib(old_lib_file)
    print('Parsing new lib file...')
    new_lib = parse_itunes_lib(new_lib_file)
    
    # Next let's figure out what tracks are missing overall
    print('Comparing libraries as a whole...')
    not_in_new, not_in_old = music_diff(old_lib, new_lib)
    
    # And finally look at the playlists
    print('Comparing individual playlists...')
    old_plists = dict()
    new_plists = dict()
    for plist in old_lib['Playlists']:
        matched_plists = match_playlists(plist, new_lib['Playlists'])
        old_plists[plist['Name']] = {'mine':plist, 'matched':matched_plists}
    for plist in new_lib['Playlists']:
        matched_plists = match_playlists(plist, old_lib['Playlists'])
        new_plists[plist['Name']] = {'mine':plist, 'matched':matched_plists}
        
    if log_file is not None:
        logf = open(log_file, 'w')
        write_fxn = lambda s: logf.write(s+'\n')
    else:
        write_fxn = lambda s: print(s)
    
    sec_sep = '\n##########################\n'
    
    # Now write the report
    write_fxn('Summary:')
    write_fxn('Tracks in the old library, {}: {}'.format(old_lib_file, len(old_lib['Tracks'])))
    write_fxn('Tracks in the new library, {}: {}'.format(new_lib_file, len(new_lib['Tracks'])))
    
    write_fxn(sec_sep)
    write_fxn('Tracks missing from the new library:')
    for track in not_in_new:
        write_fxn('   {}'.format(format_track(track)))
    write_fxn('\n')
    write_fxn('Tracks missing from the old library:')   
    for track in not_in_old:
        write_fxn('   {}'.format(format_track(track)))
        
    write_fxn(sec_sep)
    write_fxn('Comparing playlists found in the old library:')
    
    skip_lists = ['Library', 'Music', 'Genius']
    
    lists_alphabetical = old_plists.keys()
    lists_alphabetical.sort()
    for k in lists_alphabetical:
        if k in skip_lists:
            # avoid the very long catch-all lists
            continue
        if len(old_plists[k]['matched']) != 1:
            write_fxn('   Playlist {} matches {} playlists in the new library'.format(k, len(old_plists[k]['matched'])))
        else:
            old_ptracks = assemble_playlist(old_plists[k]['mine'], old_lib['Tracks'])
            new_ptracks = assemble_playlist(old_plists[k]['matched'][0], new_lib['Tracks'])
            write_fxn('   Playlist {}:'.format(k))
            all_tracks = True
            for t in old_ptracks:
                if not track_in_list(t, new_ptracks):
                    write_fxn('      {} missing from new playlist'.format(format_track(t)))
                    all_tracks = False
            if all_tracks:
                write_fxn('      All tracks accounted for')
    
        
    if log_file is not None:
        logf.close()
    