#from distutils.filelist import findall
import subprocess
import re
import json
import TX_to_Address

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
    for i in range(0, len(txlist), 1):

        data = {}
        pointer = []
        #getrawtransaction으로 해당 트랜잭션의 정보를 hex값으로 얻어옴
        getrawtx = str(nodecmd("getrawtransaction", txlist[i]))
        #hex값 해독
        txinfo = str(nodecmd("decoderawtransaction", getrawtx))
        #vin 개수
        count_vin = txinfo.count("vin")

        #vin만 파싱하게끔 바꿔야됨
        vinmatch = re.compile('\[[^]]*\]')#정규표현식 수정하기
        vin = vinmatch.findall(txinfo)
        pointermatch = re.compile("[a-z0-9]{63,64}")
        pointer = pointermatch.findall(str(vin))

        
        data['Info'] = txlist[i]
        data['Pointer'] = pointer[0:count_vin]
        file_path = TxdbPath + blocknumber+'.json'
        with open(file_path, 'a') as f : 
            json.dump(data, f)
        #반드시 json파일 다 지운다음에 할 것!


def searchnexttx(searchtxinfo, blocknumber):
    list = []
    for s in range(1, blocknumber, 1):
        stostring = s

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
        if i==103 :
            print("")
        savetx(txlist, str(i))

    
    searchnexttx(searchtx, blocknumber)

if __name__ == '__main__':
    main()