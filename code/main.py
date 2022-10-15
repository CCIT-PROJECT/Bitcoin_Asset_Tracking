#from distutils.filelist import findall
import subprocess
import re
import json
import TX_to_Address
from anytree import Node, RenderTree

#daemon까지가 들어가서 실행
#bitcoind.exe -regtest -datadir="../data" -rpcport=1234 -port=8881 -txindex

# 함수
def nodecmd(command, option):
    node = Path + "-regtest -rpcport=1234 -datadir="+DataPath
    output = subprocess.getoutput(node +" "+ command +" "+ option)
    return output

def getblockchaininfo():
    output = nodecmd("getblockchaininfo ", "\n")
    matchblocknum = re.compile('[0-9]+')
    txs = matchblocknum.findall(output)
    blocknumber = int(txs[0])
    return blocknumber

def loadblock(blocknumber):
    #원하는 블록의 해시값을 가져옴
    blockhash = nodecmd("getblockhash", str(blocknumber))

    #해당 블록의 정보를 가져옴
    blockinfo = nodecmd("getblock", str(blockhash))

    #정규표현식 파싱을 통해 블록의 트랜잭션 값만 가져옴
    matchtxs = re.compile('\\[[^]]*\\]')
    txs = matchtxs.findall(blockinfo)

    #"" 안에 값만 추출
    matchtx = re.compile('"([^"]*)"')
    txlist = matchtx.findall(str(txs))
    return txlist

def savetx(txlist, blocknumber):
    data = {}
    for i in range(0, len(txlist), 1):

        
        #getrawtransaction으로 해당 트랜잭션의 정보를 hex값으로 얻어옴
        getrawtx = str(nodecmd("getrawtransaction", txlist[i]))
        #hex값 해독
        txinfo = str(nodecmd("decoderawtransaction", getrawtx))
        #vin 개수
        count_vin = txinfo.count("vin")

        #vin,vout 파싱
        vinmatch = re.compile('\[[^]]*\]')
        vin = vinmatch.findall(txinfo)

        #tx pointer값 가져오기
        pointermatch = re.compile("[a-z0-9]{63,64}")
        pointer = pointermatch.findall(str(vin))

        data[i] = {'Info' : txlist[i], 'Pointer' : pointer[0:count_vin]}



    file_path = TxdbPath + blocknumber+'.json'
    with open(file_path, 'w') as f : 
        json.dump(data, f)


def searchnexttx(searchtxinfo, blocknumber,tree):
    i = 0
    nexttxlist = []
    for i in range (1, blocknumber+1):
        #1 ~ 마지막 블록까지 저장해놓은 json파일을 불러옴
        json_data = {'Info','Pointer'}
        with open(TxdbPath + str(i) +".json",'rb') as f:
            json_data = json.load(f)
        for j in range (0,len(json_data)):
            for k in range (0,len(json_data[str(j)]['Pointer'])):
                if json_data[str(j)]['Pointer'][k] == searchtxinfo:
                    nexttxlist.append(json_data[str(j)]['Info'])

                    #json파일을 불러온 후, pointer값이 searchtxinfo와 같으면, info값을 list에 추가
    for i in range(0,len(nexttxlist)):
        child_Node = Node('tx',data=nexttxlist[i],parent=tree)
        tree = searchnexttx(nexttxlist[i],blocknumber,child_Node)#뭔가 이상 수정필요

def tx_to_walletAddress(tx_address):
    raw_tx_result = nodecmd("getrawtransaction", tx_address) #getrawtransaction result
    decode_tx_result= nodecmd("decoderawtransaction", raw_tx_result) #decoderawtransaction result

    address_parser1 = re.compile('"address": "[a-z0-9]{30,35}')
    address_parser1_result = address_parser1.findall(decode_tx_result)
    #address "wallet_address" 부분 파싱해서 가져오기

    address_parser2 = re.compile('[a-z0-9]{30,35}')
    address_parser2_reuslt = address_parser2.findall(str(address_parser1_result))
    #wallet_address만 파싱

    return address_parser2_reuslt
    

# 메인 함수
def main():
    global Path
    Path = "C:\\Users\\JaeKyeom\\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\BitcoinCore\\daemon\\bitcoin-cli "
    global TxdbPath
    TxdbPath = "C:\\Users\\JaeKyeom\\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\TXDB\\ "
    global DataPath
    DataPath = "C:\\Users\\JaeKyeom\\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\BitcoinCore\\data "
    blocknumber = getblockchaininfo()
    searchtx = str(input("searchtx: "))

    for i in range(1, blocknumber+1, 1):
        txlist = loadblock(str(i))
       # savetx(txlist, str(i))

    root = Node('root',data=searchtx)
    searchnexttx(searchtx, blocknumber,root)
    copy_tree = root
    for row in RenderTree(root):
        pre, fill, node = row
        print(f"{pre}{node.name}, data: {node.data}")
    for row in RenderTree(copy_tree):
        pre, fill, node = row
        node.data = tx_to_walletAddress(node.data)
        print(f"{pre}{node.name}, data: {node.data}")

    

if __name__ == '__main__':
    main()
#4f91c18dfcdb50e68b48ff3ee89ebf42f3c7fd0d4a2b14e331691829a7f22313
#c5381a2bad8dd0623ba63d7bf1b050cceb58f1a018d8aad4dcc6aa89a09710bd