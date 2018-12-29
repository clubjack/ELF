from pathlib2 import Path
import os
import json
import re
import shutil
leveDataFile = Path('level.txt')
structureFile = Path('structure3.txt')

levelStructure = json.loads(structureFile.read_text())

def modLevel(levelsdata,leveldata):
    for i,level in enumerate(levelsdata) :
        if level['worldNumber']==leveldata['worldNumber'] and level['levelIndex']==leveldata['levelIndex']:
            leveldata['globalLevelNumber']=level['globalLevelNumber']
            levelsdata[i]=leveldata
    return levelsdata


def getRePattern(levelStructure,nameprefix=''):
    '''
    将文件中保存的配置转换成正则表达式的匹配模板
    '''
    pattern = ''
    for key in levelStructure:
        if isinstance(levelStructure,str):
            if levelStructure.startswith('name='):
                tempP = '(?P={name})'.format(name=levelStructure[len('name='):])
        elif isinstance(levelStructure[key],list):
            if isinstance(levelStructure[key][0],dict):
                tempP = '(?P<{name}>{key}:\\s*\\[?({dictpattern})*\\]?)'.format(name=nameprefix+key,key=key,dictpattern='- '+getRePattern(levelStructure[key][0],nameprefix+key))
            elif levelStructure[key][0]=='str':
                tempP = '(?P<{name}>{key}:\\s*({dictpattern})*)'.format(name=nameprefix+key,key=key,dictpattern='- \\w*\\s*')
        elif isinstance(levelStructure[key],dict):
            tempP = '(?P<{name}>{key}:\\s*{dictpattern})'.format(name=nameprefix+key,key=key,dictpattern=getRePattern(levelStructure[key],nameprefix+str(key)))
            # print(tempP)
        elif levelStructure[key]=='int':
            tempP = '(?P<{name}>{key}:\\s*-?\\d*)'.format(name=nameprefix+key,key=key)
            
        elif levelStructure[key]=='.':
            tempP = '(?P<{name}>{key}:\\s*.*)'.format(name=nameprefix+key,key=key)
        pattern+=(tempP+'\\s*')
    return pattern




# print(repattern)
def do():
    repattern = getRePattern(levelStructure)
    re_type = re.compile(repattern,re.MULTILINE|re.DOTALL)
    levelsdata={}
    
    for (dirpath, dirnames, filenames) in os.walk('levelconfig/'):
        for filename in filenames:
            # print('starting with {filename}'.format(filename=filename))
            fname = 'levelconfig/'+filename
            if not Path(fname).exists():
                print('file {filename} not exists'.format(filename=fname))
                return
            temptext = Path(fname).read_text(encoding='utf-8')
            m = re_type.search(temptext)
            if m:
                worldNumber = m.group('worldNumber').split(':')[1].strip()
                levelIndex = m.group('levelIndex').split(':')[1].strip()
                leveldata={}
                for key in levelStructure:
                    leveldata[key]=m.group(key).split(':',1)[1].strip()
                world = levelsdata.get('world'+worldNumber,{})
                world['level'+levelIndex]=leveldata
                levelsdata['world'+worldNumber]=world
            else:
                print(fname+' level data not found!')
    return levelsdata



def exportLevelDataFromFile(leveldatafile,structurefile):
    '''
    从一个文件中导出关卡配置
    '''
    with open(structureFile,encoding='utf-8') as f:
        structure = json.loads(f.read())
    with open(leveldatafile,encoding='utf-8') as f:
        dataStr = f.read()
    result = dealwith(dataStr,structure)
    # print(result)
    # ['giftinfo','dotsToSpawn','goals','tutorialText','board']
    result['giftInfo']=dealgiftInfo(result['giftInfo'])
    result['dotsToSpawn']=dealdotsToSpawn(result['dotsToSpawn'])
    result['goals']=dealgoals(result['goals'])
    result['tutorialText']=dealtutorialText(result['tutorialText'])
    result['tutorialText2']=dealtutorialText(result['tutorialText2'])
    result['board']=dealboard(result['board'])
    return result

def dealgiftInfo(giftInfo):
    giftInfostructure = {'inventoryInfo':'.','popupTitle':'.','popupMessage':'.','popupMessage2':'.'}
    return dealwith(giftInfo,giftInfostructure)
def dealdotsToSpawn(dotsToSpawn):
    dotsToSpawnstructure = {'dotType':'int','colorType':'int','number':'int'}
    dots=[x for x in dotsToSpawn.split('-') if x]
    for i in range(len(dots)):
        dots[i]=dealwith(dots[i],dotsToSpawnstructure)
    return dots
def dealgoals(goals):
    goalsstructure = {'type':'int','amount':'int','progress':'int'}
    result=[x for x in goals.split('-') if x]
    for i in range(len(result)):
        result[i]=dealwith(result[i],goalsstructure)
    return result
def dealtutorialText(tutorialText):
    if tutorialText=='[]':
        return []
    return [x.strip() for x in tutorialText.split('-') if x.strip()]
def dealboard(board):
    cellstructure = {'dot':".",'tile':'.','overlays':'.','mechanics':'.'}
    dotstructure = {'dotType':'int','colorType':'int','number':'int'}
    tilestructure = {'tileType':'int','hitPoints':'int'}
    overlaystructure = {'move':'int','type':'int','row':'int','col':'int'}
    mechanicstructure = {'mechanicType':'int','row':'int','col':'int','number':'int'}
    result = ['- dot:'+x for x in board.split('- dot:') if x]
    for i in range(len(result)):
        cell = dealwith(result[i],cellstructure)
        cell['dot']=dealwith(cell['dot'],dotstructure)
        cell['tile']=dealwith(cell['tile'],tilestructure)
        overlays = [x for x in cell['overlays'].split('-') if x]
        for j in range(len(overlays)):
            overlays[j]=dealwith(cell['overlays'],overlaystructure)
        cell['overlays']=overlays
        mechanics = [x for x in cell['mechanics'].split('-') if x]
        for j in range(len(mechanics)):
            mechanics[j]=dealwith(cell['mechanics'],mechanicstructure)
        cell['mechanics']=mechanics
        result[i]=cell
    return result
def dealwith(target,structure):
    if target=='[]':
        return
    pattern = getRePattern(structure)
    p = re.compile(pattern,re.DOTALL)
    m=p.search(target)
    result={}
    if m:
        for key in structure:
            result[key]=m.group(key).split(':',1)[1].strip()
    else:
        result=target
    return result



levelsdata = json.loads(Path('leveldata6.json').read_text())
# for i in range(25):
#     filename = 'leveldata_2_{}(2).txt'.format(i)
#     leveldata = exportLevelDataFromFile(filename,'structure3.txt')
#     levelsdata=modLevel(levelsdata,leveldata)
# print(levelsdata[35])
# Path('leveldata6.json').write_text(json.dumps(levelsdata))
# # print(exportLevelDataFromFile('leveldata_2_0(2).txt','structure3.txt'))
# globalLevelNumber=1

temp = set()
for level in levelsdata:
    worldN = level['worldNumber']
    levelN = level['levelIndex']
    movesToAddForRebalance = level['movesToAddForRebalance']
    HUDInfo = level['HUDInfo']
    giftInfo = level['giftInfo']
    levelIntent = level['levelIntent']
    eventID = level['eventID']
    excludedPowerUpTypes = level['excludedPowerUpTypes']
    width = level['width']
    height = level['height']
    dotType = [x['dot']['dotType'] for x in level['board']]
    number = [x['dot']['number'] for x in level['board']]
    tileType = [x['tile']['tileType'] for x in level['board']]
    mechanics = [str(x['mechanics']) for x in level['board'] if x['mechanics']!=[None]]
    overlays = [str(x['overlays']) for x in level['board'] if x['overlays']!=[None]]
    tutorialText = level['tutorialText']
    if tutorialText: print('\n'.join(tutorialText))
    dots = [x['dot'] for x in level['board']]
    if level['globalLevelNumber'] in range(480,490):print(set(dotType),set(tileType),set(overlays),set(mechanics))
    # if int(worldN) in [0,1,2,3]: print(worldN,levelN)
    temp.update(tutorialText)
# levels=[]
# for world in range(50):
#     worldN='world'+str(world)
#     if worldN in levelsdata:
#         for level in range(25):
#             levelN='level'+str(level)
#             print(worldN,levelN)
#             if levelN in levelsdata[worldN]:
#                 levelsdata[worldN][levelN]['globalLevelNumber']=globalLevelNumber
#                 levels.append(levelsdata[worldN][levelN])
#                 globalLevelNumber+=1


        
        
# Path('leveldata4.json').write_text(json.dumps(levelsdata))            
# Path('leveldata5.json').write_text(json.dumps(levels))            
# print(dealtutorialText(levelsdata['world0']['level1']['tutorialText']))
# print('\n'.join(temp))