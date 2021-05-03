import requests
import pandas
import urllib.parse # Replace %xx escapes by their single-character equivalent.
import datetime

world_name = 'ru70'
world_server = 'https://' + world_name + '.voyna-plemyon.ru/map'
world_data_url = ['/village.txt.gz', '/player.txt.gz', '/ally.txt.gz','/conquer.txt.gz','/kill_all.txt.gz','/kill_def.txt.gz','/kill_sup.txt.gz']
pathname = 'dl'

for filename in world_data_url:
    print(filename)
    with open(pathname + filename, 'wb') as f:
        url = world_server + filename
        r = requests.get(url)
        f.write(r.content)

data_village = pandas.read_csv(pathname + '/village.txt.gz', compression='gzip', header=None, keep_default_na=False, names=['village_id', 'village_name', 'xxx', 'yyy', 'player_id', 'village_points', 'rank'])
for i in range(len(data_village.iloc[:, 1])):
    data_village.iloc[i, 1] = urllib.parse.unquote_plus(data_village.iloc[i, 1])

#$player_id, $name, $tribe_id, $villages, $points, $rank
data_player = pandas.read_csv(pathname + '/player.txt.gz', compression='gzip', header=None, names=['player_id', 'player_name', 'tribe_id', 'villages', 'player_points', 'rank'])
for i in range(len(data_player.iloc[:, 1])):
    data_player.iloc[i, 1] = urllib.parse.unquote_plus(data_player.iloc[i, 1])

#$tribe_id, $name, $tag, $members, $villages, $points, $all_points, $rank
data_ally = pandas.read_csv(pathname+'/ally.txt.gz', compression='gzip', header=None,
                            names=['tribe_id', 'tribe_name', 'tag', 'members', 'villages', 'tribe_points', 'tribe_all_points', 'rank'])
for i in range(len(data_ally.iloc[:, 1])):
    data_ally.iloc[i, 1] = urllib.parse.unquote_plus(data_ally.iloc[i, 1])
    data_ally.iloc[i, 2] = urllib.parse.unquote_plus(data_ally.iloc[i, 2])
    
merge_village_player = data_village.merge(data_player,on='player_id')
merge_village_player_ally = merge_village_player.merge(data_ally,on='tribe_id')
merge_village_player_ally["xxx|yyy"] = merge_village_player_ally["xxx"].map(str) + '|' + merge_village_player_ally["yyy"].map(str)
#print(merge_village_player_ally.iloc[:10,:])

output_frame = pandas.concat([merge_village_player_ally.loc[:,'xxx|yyy'],merge_village_player_ally.loc[:,'player_name'],merge_village_player_ally.loc[:,'tag'],
                              merge_village_player_ally.loc[:,'village_points'],merge_village_player_ally.loc[:,'player_points'], merge_village_player_ally.loc[:,'village_id'],
                              merge_village_player_ally.loc[:,'player_id'], merge_village_player_ally.loc[:,'tribe_id'], merge_village_player_ally.loc[:,'village_name']],axis=1)
#print(output_frame.iloc[:10,:])
pathname = 'c:/Users/leb61ww/Downloads/'
output_frame.to_csv(pathname+'/data-' + world_name + '-'+datetime.datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss')+'.csv',encoding='utf-8-sig')

# https://erikrood.com/Posts/py_gsheets.html
import pygsheets
#authorization
gc = pygsheets.authorize(service_file='client_secret.json')

#open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
sh = gc.open_by_key('1PQ4lrca7zkXg8x3WF4ADDR_Z5JqNXbwRjSl7_7EjXqA')

#select the first sheet 
wks = sh[0]

#update the first sheet with df, starting at cell B2. 
wks.set_dataframe(output_frame,(1,2))
