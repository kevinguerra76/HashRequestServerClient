import struct
import sys
import socket
import select
import hashlib

#Kevin Guerra

def create_struct(short_int1, long_int1, long_int2, str_32_byte):
    # This function will be used to create a universal struct object
    message = struct.pack('!HLL32s', short_int1, long_int1, long_int2, str_32_byte)
    return message
    

def open_struct(struct_obj):
    # This function will be used to open a universal struct object
    message = struct.unpack('!HLL32s', struct_obj)
    return message  # Returns array [short, long, long, 32-byte string]


def create_acknowledgement(input_n):
    # This function retrieves the S value from the initialization message
    # Then, return acknowledgement message
    
    # Write your logic  
    empty_binary = bytes()
    message =  create_struct(2, 0, 40*input_n, empty_binary) #from pdf 
    return message


def check_initialization(encoded_data):
    try:
        type_val, S, length, data = open_struct(encoded_data)
        #num_hash_requests = socket.ntohl('TODO')  # Block sizes this client will send
        #type_val = socket.ntohs('TODO')
        if type_val != 1:
            print("SERVER: Invalid Type Value")
            return False
        return S
    except:
        print("SERVER: Invalid Data Format")
        return False

def make_hash(data):
    h = hashlib.sha256() #use secure hashing 256
    h.update(data.encode()) #update the data (which must be encoded because it was made into a string when adding the salt   
    hashed_data = h.hexdigest()

    return str(hashed_data)

def check_hash_request(encoded_data):
    try:
        type_val, S, length, data = open_struct(encoded_data)
        #type_val = socket.ntohs(int.from_bytes(initial_message, byteorder='big'))
        if type_val != 3:
            print("SERVER: Invalid Type Value")
            return False 
        return True # Struct Object
    except:
        print("SERVER: Invalid Data Format")
        return False


def get_hashed_data(hash_request , salt = ''):
    # This function will receive an unpacked struct representing our hash request
    # Then, return hashed data and hash response

    # Extract variables
    try:
        request_type, i, length, payload = open_struct(hash_request)
    except:
        return False
    #If this was an initialization request
    input_n = False
    if(request_type == 1):
        input_n = check_initialization(hash_request)
    if(input_n): 
        return create_acknowledgement(input_n),input_n #Return the input_n as well so the server knows the size of messages
    
    payload = str(payload) + salt # HashRequest Data + UTF-8 Encoded Salt
    hash_and_salt = make_hash(payload)
    if(check_hash_request(hash_request)):
        i += 1
        message = create_struct(4, i, 32, hash_and_salt.encode())
        return message
    return False

def start_server(port):
    # This function will create our TCP Server Socket, start listening, then return the Socket Object

    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Use parameters for IPv4 (socket.AF_INET) and for TCP (socket.SOCK_STREAM)
    tcp_server_socket.setblocking(1)  # Allow multiple connections, To allow multiple connections, the server should NOT be blocked (not be waiting for client response)
    tcp_server_socket.bind(('localhost', port))  # Start listening! Bind it to localhost (can use gethostname() for outside use)
    tcp_server_socket.listen(10)  # 10 is the max number of queued connections allowed
    return tcp_server_socket


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Variables we need
    if(len(sys.argv) < 5): # Need at least 5 arguments (itself, '-p', port#, '-s', saltv)
        sys.exit('Error need more arguments:\n-p, port#, -s, saltv (no the commas)')
    try:
        server_port = int(sys.argv[2])  # Extract server port from command line arguments
        #Also will check if the value matches what the pdf said and the maximum for a tcp port#
        if server_port < 1024 or server_port > 65535:
            raise Exception()
    except: #IF user did not give a vlid integer or gave a port too high or low
        sys.exit('Error, port# must be a valid integer (1024 < port# < 65,535)')
    hash_salt = sys.argv[4]  # Extract salt value from command line arguments (can stay as a string)

    server_socket = start_server(server_port)
    clients = [server_socket]
    n_sizes = {} # this dictionary will work like this: 'client_name' -> client_addr, so when selecting I also get addr

    print("Server listening...")

    ## WRITE YOUR CODE TO IMPLEMENT SERVER SIDE PROTOCOL LOGIC
    ## USE select() to handle multiple clients
    while(1):
        print('Waiting for connection')
        client, addr = server_socket.accept()
        clients.append(client)
        print('Connected')
        #Send the acknowledgement to the user after accepting the connection
        data = client.recv(42) #Get the initializaition (is 42 because that is the size of the struct)
        client_ack,input_n = get_hashed_data(data, hash_salt)
        n_sizes[client] = {addr,input_n}
        client.send(client_ack) #Send ack

        '''
        could not figure out how to use select, I am not sure how to test for it but one client does work at once
        I do not know how to work with concurrent programs too well yet 
        '''
        curr_client = select.select(clients,clients, clients, 1) #select a random client from the clients list
        addr, input_n = n_sizes[client]
        #Now get ready to recieve the payloads from the clients
        while(1):
            client_request = client.recv(42) 
            client_hash = get_hashed_data(client_request, hash_salt)
            if(not client_hash): #If the client hash returned False, then break out of this for loop because all the data was sent
                break
            client.send(client_hash)
    
    server_socket.close() #Close the socket at the end if at any point the while loop breaks
       
            




    
