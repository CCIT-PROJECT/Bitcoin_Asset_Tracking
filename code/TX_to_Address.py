import re
import os
import json

def nodecmd(cmd) :
    node = "C:\\Users\\JaeKyeom\\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\BitcoinCore\\daemon\\bitcoin-cli -regtest -rpcport=1234 -datadir=C:\\Users\\JaeKyeom\\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\BitcoinCore\\data "
    result = os.popen(node + cmd).read()
    return result

def tx_to_walletAddress(tx_address):
    raw_tx_result = nodecmd("getrawtransaction "+ tx_address) #getrawtransaction result
    decode_tx_result= nodecmd("decoderawtransaction " + raw_tx_result) #decoderawtransaction result

    address_parser1 = re.compile('"address": "[a-z0-9]{30,35}')
    address_parser1_result = address_parser1.findall(decode_tx_result)
    #address "wallet_address" 부분 파싱해서 가져오기

    address_parser2 = re.compile('[a-z0-9]{30,35}')
    address_parser2_reuslt = address_parser2.findall(str(address_parser1_result))
    #wallet_address만 파싱

    return address_parser2_reuslt


def searchnexttx() :
    with open("D:\\Bitcoin\\txinfo\\"+"1.json",'r') as f:
        json_data = json.loads(f)#loads 써보자
    print((json_data))
    # for i in range(1, blocknumber+1) :
    #     pass

def main():
    
    #os.system("C:\\Users\\JaeKyeom\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\BitcoinCore\\daemon\\bitcoind.exe -regtest -txindex -rpcport=1111 -datadir=C:\\Users\\JaeKyeom\\Desktop\\Bitcoin_Asset_Tracking\\Bitcoin_Asset_Tracking\\BitcoinCore\\data -port=8881")
    # print(nodecmd("getrawtransaction 784c7115114ff74d49ad2624f4d520c2f60fb3ebb8480834c7c51c1427dcffa2"))
    wallet_address_list = tx_to_walletAddress("4f91c18dfcdb50e68b48ff3ee89ebf42f3c7fd0d4a2b14e331691829a7f22313")
    print(wallet_address_list)
    searchnexttx()


if __name__ == '__main__' :
    main()