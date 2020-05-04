# Ruby wallet
# Coded by Adrijan Petek

import requests, json, hashlib, random, os, binascii, ecdsa, base58, time, hmac, multiprocessing, pyperclip, PySimpleGUI as sg, time

print('Starting...')

def secret():
    return binascii.hexlify(os.urandom(32)).decode('utf-8').upper()

def pubkey(secret_exponent):
    privatekey = binascii.unhexlify(secret_exponent)
    s = ecdsa.SigningKey.from_string(privatekey, curve = ecdsa.SECP256k1)
    return '04' + binascii.hexlify(s.verifying_key.to_string()).decode('utf-8')
def add(public_key):
    output = []; alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    var = hashlib.new('ripemd160')
    var.update(hashlib.sha256(binascii.unhexlify(public_key.encode())).digest())
    var = '00' + var.hexdigest() + hashlib.sha256(hashlib.sha256(binascii.unhexlify(('00' + var.hexdigest()).encode())).digest()).hexdigest()[0:8]
    count = [char != '0' for char in var].index(True) // 2
    n = int(var, 16)
    while n > 0:
        n, remainder = divmod(n, 58)
        output.append(alphabet[remainder])
    for i in range(count): output.append(alphabet[0])
    return ''.join(output[::-1])

def wif(secret_exponent):
    var80 = "80"+secret_exponent
    var = hashlib.sha256(binascii.unhexlify(hashlib.sha256(binascii.unhexlify(var80)).hexdigest())).hexdigest()
    return str(base58.b58encode(binascii.unhexlify(str(var80) + str(var[0:8]))), 'utf-8')


def get():
    URL = 'https://www.bitstamp.net/api/ticker/'
    try:
        r = requests.get(URL)
        priceFloat = float(json.loads(r.text)['last'])
        return priceFloat
    except requests.ConnectionError:
        print ("Error querying Bitstamp API")



        
sg.ChangeLookAndFeel('Black')
layout =  [
            [sg.Text('Date & Time:   ', font=('Comic sans ms', 18)),sg.Text('', size=(60,1), font=('Comic sans ms', 14), key='_DATE_')],
            [sg.Text('1 BTC = USD:  ', font=('Comic sans ms', 18)), sg.Text('', size=(60,1), font=('Comic sans ms', 14),  key='coin')],
            [sg.Text(''), sg.Image('btc.png', size=(250, 250))],
            [sg.Text('Anonymous Ruby wallet for bitcoin', size=(60,1), font=('Comic sans ms', 18), text_color='blue')],
            [sg.Text('Address:      ', font=('Comic sans ms', 18)), sg.Text('', size=(100,1), font=('Comic sans ms', 14),  key='generator')],
            [sg.Text('Privatekey: ',font=('Comic sans ms', 18)), sg.Text('', size=(100,1), font=('Comic sans ms', 14), key='privatekey')],
            [sg.Text('Publickey:  ',font=('Comic sans ms', 18)), sg.Text('', size=(140,1), font=('Comic sans ms', 14), key='publickey')],
            [sg.Text('WIF:         ', font=('Comic sans ms', 18)), sg.Text('', size=(100,1), font=('Comic sans ms', 14), key='wif')],
            [sg.Button('Create', font=('Comic sans ms', 18), button_color=('white', 'blue')), sg.Button('Exit', font=('Comic sans ms', 18), button_color=('white', 'red'))]]


window = sg.Window('Ruby wallet',
                  layout=layout,
                   default_element_size=(12,1),
                   font='Helvetica 18',
                   )

time = time.ctime()
#  The "Event loop" where all events are read and processed (button clicks, etc)




while True:
    secret_exponent = secret()
    public_key = pubkey(secret_exponent)
    address = add(public_key)
    coinprice = get()
    WIF = wif(secret_exponent)
    
    event, values = window.Read(timeout=10)     # read with a timeout of 10 ms
    if event == 'Create': # if got a real event, print the info
        data = open("Wallet.txt","a")
        data.write("Wallet: "+"\n\n" + "Privatekey: " +str(secret_exponent)+"\n"+"Publickey:  " + str(public_key)+"\n"+"Address:    "+str(address)+"\n"+"WIF:        " +str(WIF)+"\n\n"+'-------------------------------------------------------------------------------------------------------------'+"\n\n")
        data.close()
        window.Element('generator').Update(str(address))
        window.Element('privatekey').Update(str(secret_exponent))
        window.Element('publickey').Update(str(public_key))
        window.Element('wif').Update(str(WIF))


        # also output the information into a scrolling box in the window
        # window.Element('_MULTIOUT_').Update(str(event) + '\n' + str(values), append=True)
    # if the "Exit" button is clicked or window is closed then exit the event loop
    if event in (None, 'Exit'):
        break
    # Output the "uptime" statistic to a text field in the window
    window.Element('_DATE_').Update(str(time))
    window.Element('coin').Update(str(coinprice))

# Exiting the program
window.Close()    # be sure and close the window before trying to exit the program
print('Completed shutdown')
