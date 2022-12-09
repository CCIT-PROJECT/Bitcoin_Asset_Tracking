#from distutils.filelist import findall
import subprocess
import re
import json
from anytree import Node, RenderTree,exporter
import csv
import os


#daemon까지가 들어가서 실행
#bitcoind.exe -regtest -datadir="../data" -rpcport=1234 -port=8881 -txindex

# 함수
def nodecmd(command, option):
    # node = Path + "-regtest -rpcport=1234 -datadir="+DataPath
    node = Path + "-regtest -rpcport=1234 -datadir="+DataPath
    try:
        output = subprocess.getoutput(node +" "+ command +" "+ option)
    except:    # 예외가 발생했을 때 실행됨
        output = 'error'
    
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
        if txinfo != 'error' :
            
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
    for i in nexttxlist:
        child_Node = Node(i,data=tx_to_walletAddress(i),parent=tree)

        for n in range(len(addressData)):
            if (child_Node.data[0] == addressData[n][0]) or (child_Node.data[1] == addressData[n][0]) :
                child_Node.name = addressData[n][1]
                break
            else:
                if n == len(addressData)-1:
                    searchnexttx(i,blocknumber,child_Node)
        
        
        

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

    #638692 ~ 643484
    #for i in range(638690, blocknumber+1, 1):
    for i in range(1, blocknumber+1,1):
        if not os.path.isfile(TxdbPath+str(i)+".json") :
            txlist = loadblock(str(i))
            savetx(txlist, str(i))


    f = open('WalletAddress.csv','r',encoding='utf-8')
    global addressData
    addressData = list()
    rea = csv.reader(f)
    for row in rea:
        addressData.append(row)
    f.close
    #walletAddress -> list 형태로 변환

    root = Node('root',data=searchtx)
    searchnexttx(searchtx, blocknumber,root)
    # copy_tree = root
    for row in RenderTree(root):
        pre, fill, node = row
        print(f"{pre}{node.name}, data: {node.data}")
    print("\n\n")
    # for row in RenderTree(copy_tree):
    #     pre, fill, node = row
    #     node.name = tx_to_walletAddress(node.name)
    #     # node.data = tx_to_walletAddress(node.data)
    #     print(f"{pre}{node.name}, data: {node.data}")
    exporter.DotExporter(root).to_picture("test.png")

    

if __name__ == '__main__':
    main()
#181420f3e6f6207058db8ea9f7379bc6c0d4552acf2db8f4ce57968bb449b33f
#graphviz lib 설치 필요 pip로 하면 안되고 https://graphviz.org/download/