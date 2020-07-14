# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:28:39 2020

@author: ahmad
"""
  
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 16:13:30 2020
Create a blockchain
@author: ahmad
"""

import datetime
import hashlib
import json
from flask import Flask,request,jsonify
import requests
from uuid import uuid4
from urllib.parse import urlparse

#part 1 Building a blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transaction = []
        self.node = set()
        self.create_block(proof = 1, previous_hash = '0')
    
    def create_block(self, proof, previous_hash):
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'transactions':self.transaction}
        self.transaction = []
        self.chain.append(block)
        return block
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof = True
            else:
                new_proof +=1
        return new_proof
    
    def hash(self,block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self,sender,reciever,amount):
        self.transaction.append({'sender':sender,
                                 'reciever':reciever,
                                 'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1
     
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        
        max_length = len(self.chain)
        network = self.node
        longest_chain = None   
        for node in network:
            response = requests.get(f'http:{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length>max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        

#part 2 Mining our blockchain
        
app = Flask(__name__)

node_address = str(uuid4()).replace('-','');
blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
     previous_block = blockchain.get_previous_block()
     previous_proof = previous_block['proof']
     proof = blockchain.proof_of_work(previous_proof)
     previous_hash = blockchain.hash(previous_block)
     blockchain.add_transaction(sender = node_address, reciever = 'Ahmad', amount = 1)
     block = blockchain.create_block(proof,previous_hash)
     response = {'message': 'new block mined!',
                 'index':block['index'],
                 'timestamp':block['timestamp'],
                 'proof':block['proof'],
                 'previous_hash':block['previous_hash'],
                 'transactions':block['transaction']}
     return jsonify(response),200 
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = requests.get_json();
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'bad request',400
    index = blockchain.add_transaction(json['sender'], json['reciever'], json['amount'])
    res = {'message':f'your transaction will be added in block {index}'}
    return jsonify(res),201
@app.route('/get_chain',methods = ['GET'])
def get_chain():
    response = {'chain':blockchain.chain,
                'length':len(blockchain.chain)}
    return jsonify(response), 200
@app.route('/is_chain_valid', methods = ['GET'])
def validate_chain():
    chain = blockchain.chain
    if blockchain.is_chain_valid(chain):
        response = {'message': 'YES the chain is valide'}
    else:
        response = {'message': 'We are in trouble the blockchain is not valid'}
    return jsonify(response),200
@app.route('/add_node', methods = ['POST'])
def add_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'no node',400
    for node in nodes:
        blockchain.add_node(node)
    res = {'message': 'The following nodes are in the network ',
           'nodes_list':list(blockchain.node)}
    return jsonify(res),201
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    if is_replaced:
        res = {'message': 'Chain is replaced successfully with largest chain', 'latest_chain':blockchain.chain}
    else:
        res = {'message': 'Nothing to replace current chain is the largest','latest_chain':blockchain.chain}
    return jsonify(res), 200

app.run(host = 'http://127.0.0.1',port = 5000)
 
     










































