import subprocess
import re
import json
#import TX_to_Address
from anytree import Node, RenderTree, exporter
import os

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



    file_path = TxdbPath + blocknumber + '.json'
    with open(file_path, 'w') as f : 
        json.dump(data, f)


def searchnexttx(searchtxinfo, blocknumber, tree):
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
        tree = searchnexttx(nexttxlist[i],blocknumber,child_Node)

def tx_to_walletAddress(tx_address):
    raw_tx_result = nodecmd("getrawtransaction", tx_address)
    #getrawtransaction result
    decode_tx_result= nodecmd("decoderawtransaction", raw_tx_result)
    #decoderawtransaction result

    address_parser1 = re.compile('"address": "[a-z0-9]{30,35}')
    address_parser1_result = address_parser1.findall(decode_tx_result)
    #address "wallet_address" 부분 파싱해서 가져오기
    address_parser2 = re.compile('[a-z0-9]{30,35}')
    address_parser2_reuslt = address_parser2.findall(str(address_parser1_result))
    #wallet_address만 파싱

    return address_parser2_reuslt

def visualization(tree):
    exporter.DotExporter(tree).to_picture("test.png")
    

# 메인 함수
def main():
    global Path
    Path = "C:\\Users\\smj10\\Desktop\\blockchain\\Bitcoin_Asset_Tracking\\BitcoinCore\\daemon\\bitcoin-cli "
    global TxdbPath
    TxdbPath = "C:\\Users\\smj10\\Desktop\\blockchain\\Bitcoin_Asset_Tracking\\TXDB\\"
    global DataPath
    DataPath = "C:\\Users\\smj10\\Desktop\\blockchain\\Bitcoin_Asset_Tracking\\BitcoinCore\\data "
    blocknumber = getblockchaininfo()
    searchtx = str(input("searchtx: "))
    #txdb에 파일 유무 확인
    #1은 readme
    if len(os.listdir(TxdbPath)) == 0 or len(os.listdir(TxdbPath)) == 1:
        update_savetx = "Y"
    else:
        update_savetx = str(input("Do you want to update tx?(Y/n): "))

    for i in range(1, blocknumber+1, 1):
        txlist = loadblock(str(i))
        if update_savetx == 'Y' or update_savetx == 'y':
            savetx(txlist, str(i))

    root = Node('root',data=searchtx)
    searchnexttx(searchtx, blocknumber,root)
    copy_tree = root
    
    for row in RenderTree(root):
        root.name = root.data
        pre, fill, node = row
        node.name = node.data
        print(f"{pre}{node.name}, data: {node.data}")
    print("\n\n")
    # visualization(root)
    #print("\n\n")
    
    for row in RenderTree(copy_tree):
        pre, fill, node = row
        root.name = root.data
        node.data = tx_to_walletAddress(node.data)

        node.name = node.data
        print(f"{pre}{node.name}, data: {node.data}")
    visualization(root)

    

if __name__ == '__main__':
    main()
#f4fd2ac3e1dde46baaa734b9a5ca9108a0523cc94f5e4e690d2b3c6a45a794cc