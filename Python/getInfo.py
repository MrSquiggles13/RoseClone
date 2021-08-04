# %%
import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

# %%


def getInfo(contract, burn_address):

    headers = {'X-API-KEY': os.getenv('BITQUERY_KEY')}
    query = (
        'query MyQuery {'
        '  ethereum(network: bsc) {'
        '    BNB: dexTrades('
        '      options: {desc: ["block.height", "tradeIndex"], limit: 1}'
        '      exchangeName: {in: ["Pancake", "Pancake v2"]}'
        '      baseCurrency: {is: ' +
        '"{}"'.format(contract) + '}' +
        '      quoteCurrency: {is: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"}'
        '    ) {'
        '      block {'
        '        height'
        '      }'
        '      baseCurrency {'
        '        symbol'
        '        address'
        '      }'
        '      quoteCurrency {'
        '        symbol'
        '        address'
        '      }'
        '      quotePrice'
        '      tradeIndex'
        '    }'
        '    BUSD: dexTrades('
        '      options: {desc: ["block.height", "tradeIndex"], limit: 1}'
        '      exchangeName: {in: ["Pancake", "Pancake v2"]}'
        '      baseCurrency: {is: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"}'
        '      quoteCurrency: {is: "0xe9e7cea3dedca5984780bafc599bd69add087d56"}'
        '    ) {'
        '      block {'
        '        height'
        '      }'
        '      baseCurrency {'
        '        symbol'
        '        address'
        '      }'
        '      quoteCurrency {'
        '        symbol'
        '        address'
        '      }'
        '      quotePrice'
        '      tradeIndex'
        '    }'
        '    transactions {'
        '          gasValue'
        '        }'
        '        transfers('
        '          currency: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
        '          sender: {is: ' +
        '"{}"'.format(burn_address[0]) +
        '}'
        '        ) {'
        '          amount'
        '        }'
        '        autoburn: transfers('
        '         currency: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
        '          sender: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
        '          receiver: {is: ' +
        '"{}"'.format(burn_address[0]) +
        '}'
        '        ) {'
        '          amount'
        '        }'
        '        manualburn: transfers('
        '          currency: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
        '          receiver: {is: ' +
        '"{}"'.format(burn_address[1]) +
        '}'
        '        ) {'
        '          amount'
        '        }'
        '    '
        '  }'
        '}'
    )

    data = requests.post(url="https://graphql.bitquery.io",
                         json={'query': query}, headers=headers).json()['data']

    price = data['ethereum']['BNB'][0]['quotePrice'] * \
        data['ethereum']['BUSD'][0]['quotePrice']

    auto_burn = data['ethereum']['autoburn'][0]['amount']
    manual_burn = data['ethereum']['manualburn'][0]['amount']
    initial_supply = data['ethereum']['transfers'][0]['amount']
    burn_supply = auto_burn + manual_burn
    circulating_supply = initial_supply - burn_supply

    market_cap = circulating_supply * price

    req = requests.get(f"https://bscscan.com/token/{contract}")
    soup = BeautifulSoup(req.text, 'html.parser')
    text = soup.find("div", class_="mr-3")
    holders = str(text.text[1:-1])

    holders = int(holders[:-10].replace(',', ''))

    return price, market_cap, holders, circulating_supply, burn_supply


# %%
# contract = "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"
# burn_address = ["0x0000000000000000000000000000000000000000",
#                 "0x0000000000000000000000000000000000000001"]
# headers = {'X-API-KEY': os.getenv('BITQUERY_KEY')}
# query = (
#     'query MyQuery {'
#     '  ethereum(network: bsc) {'
#     '    BNB: dexTrades('
#     '      options: {desc: ["block.height", "tradeIndex"], limit: 1}'
#     '      exchangeName: {in: ["Pancake", "Pancake v2"]}'
#     '      baseCurrency: {is: ' +
#     '"{}"'.format(contract) + '}' +
#     '      quoteCurrency: {is: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"}'
#     '    ) {'
#     '      block {'
#     '        height'
#     '      }'
#     '      baseCurrency {'
#     '        symbol'
#     '        address'
#     '      }'
#     '      quoteCurrency {'
#     '        symbol'
#     '        address'
#     '      }'
#     '      quotePrice'
#     '      tradeIndex'
#     '    }'
#     '    BUSD: dexTrades('
#     '      options: {desc: ["block.height", "tradeIndex"], limit: 1}'
#     '      exchangeName: {in: ["Pancake", "Pancake v2"]}'
#     '      baseCurrency: {is: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"}'
#     '      quoteCurrency: {is: "0xe9e7cea3dedca5984780bafc599bd69add087d56"}'
#     '    ) {'
#     '      block {'
#     '        height'
#     '      }'
#     '      baseCurrency {'
#     '        symbol'
#     '        address'
#     '      }'
#     '      quoteCurrency {'
#     '        symbol'
#     '        address'
#     '      }'
#     '      quotePrice'
#     '      tradeIndex'
#     '    }'
#     '    transactions {'
#     '          gasValue'
#     '        }'
#     '        transfers('
#     '          currency: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
#     '          sender: {is: "0x0000000000000000000000000000000000000000"}'
#     '        ) {'
#     '          amount'
#     '        }'
#     '        autoburn: transfers('
#     '         currency: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
#     '          sender: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
#     '          receiver: {is: "0x0000000000000000000000000000000000000000"}'
#     '        ) {'
#     '          amount'
#     '        }'
#     '        manualburn: transfers('
#     '          currency: {is: "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"}'
#     '          receiver: {is: "0x0000000000000000000000000000000000000001"}'
#     '        ) {'
#     '          amount'
#     '        }'
#     '    '
#     '  }'
#     '}'
# )

# data = requests.post(url="https://graphql.bitquery.io",
#                      json={'query': query}, headers=headers).json()['data']

# price = data['ethereum']['BNB'][0]['quotePrice'] * \
#     data['ethereum']['BUSD'][0]['quotePrice']

# auto_burn = data['ethereum']['autoburn'][0]['amount']
# manual_burn = data['ethereum']['manualburn'][0]['amount']
# initial_supply = data['ethereum']['transfers'][0]['amount']

# circulating_supply = initial_supply - (auto_burn + manual_burn)

# market_cap = circulating_supply * price

# req = requests.get(f"https://bscscan.com/token/{contract}")
# soup = BeautifulSoup(req.text, 'html.parser')
# text = soup.find("div", class_="mr-3")
# holders = str(text.text[1:-1])

# holders = int(holders[:-10].replace(',', ''))

# price, market_cap, circulating_supply
# %%
