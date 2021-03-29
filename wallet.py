import subprocess
import json
import os
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
import bit


from constants import *

mnemonic = os.getenv('MNEMONIC', 'insert mnemonic here')



def derive_wallets(mnemonic, coin, numderive):
    command = f'./derive -g --coin={coin} --numderive={numderive} --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --format=json'

    
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()


    keys = json.loads(output)
    #print(keys)
    return (keys)

coins = {'btc-tst':derive_wallets(mnemonic, BTCTEST, 10), 'eth':derive_wallets(mnemonic, ETH, 10)}



def priv_key_to_account(coin, priv_key):
    if coin==('eth'):
        return (w3.eth.accounts.privateKeyToAccount(priv_key))
    if coin ==('btc-tst'):
        return (bit.PrivateKeyTestnet(priv_key))

def create_tx(coin, account, to, amount):
    if coin ==('eth'):
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount})
        return {
        "from": account.address,
        "to": to,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address)}
    if coin ==('btc-tst'):
        tx_data = (bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)]))
        return tx_data

def send_tx(coin, account, to, amount):
    tx = create_tx(coin, account, to, amount)
    if coin==('eth'):    
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        #print(result.hex())
        signed = result.hex()
        w3.eth.sendRawTransaction(signed.rawTransaction)
        return ('Done')
    if coin ==('btc-tst'):
        tx_data = create_tx(coin, account, to, amount)
        signed = (account.sign_transaction(tx_data))
        print(signed)
        bit.network.NetworkAPI.broadcast_tx_testnet(signed)
        return('Done')

