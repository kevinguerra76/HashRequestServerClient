import struct
import sys
import socket

#Kevin Guerra 

def create_struct(short_int1, long_int1, long_int2, str_32_byte):
    # This function will be used to create a universal struct object
    message = struct.pack('!HLL32s', short_int1, long_int1, long_int2, str_32_byte)
    return message
    

def open_struct(struct_obj):
    # This function will be used to open a universal struct object
    message = struct.unpack('!HLL32s', struct_obj)
    return message  # Returns array [short, long, long, 32-byte string]

def create_initialization(hash_requests):
    # This function will be used to create the initialization message to send to the server using struct
    # Then, return the message
    empty_binary = bytes()
    message = create_struct(1, hash_requests, 0, empty_binary) #From the pdf
    return message


def create_hash_request(hash_count, block_size, current_block):
    # This function will create a Hash Request
    # Then, return the message as a struct obj

    hash_count = hash_count
    block_len = block_size
    struct_hash_message = create_struct(3, hash_count,block_len, current_block)

    return struct_hash_message


def check_acknowledgement(encoded_data):
    try:
        type_val, i, length, data = open_struct(encoded_data)
        #type_val = socket.ntohs(int.from_bytes(initial_message, byteorder='big'))
        #print('type_val: ', type_val)
        if type_val != 2:
            print("CLIENT: Invalid Type Value")
            return False
        return length # Returns the Length from Ack Message
    except:
        print("CLIENT: Invalid Data Format")
        return False


def check_hash_response(encoded_data):
    try:
        type_val, i, length, data = open_struct(encoded_data)
        #type_val = socket.ntohs('TODO')
        if type_val != 4:
            print("CLIENT: Invalid Type Value")
            return False
        message = create_hash_request(i, length, data)
        return message # Returns Struct Object
    except:
        print("CLIENT: Invalid Data Format")
        return False

#This file will recieve the file and the size of the requests, then it will return a list with all the information
def read_file(file ,size): 
    f= open(file, "r")
    arr = []
    line = f.read(size) #Will read the first *size* bytes
    while(line):
        arr.append(line)
        line = f.read(size) #Will read the next *size* bytes
    return arr

def connect_server(ip, port):
    # This function will be used to create a socket and connect to server
    # Then, return the socket object

    ## 'TODO' - Write logic to connect to the server
    
    tcp_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Start the socket with the usual IPv4 and TCP
    tcp_socket.connect((ip, port)) 
    #tcp_socket.listen(1)

    print("Connected to server!")
    return tcp_socket


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Variables we need from the command line
    if(len(sys.argv) < 9): # Need at least 9 arguments (itself, -a, IP, -p, port#, -s, size, -f, FILE )
        sys.exit('Error need more arguments:\n-a, IP, -p, port#, -s, size, -f, FILE (no the commas)')
    server_ip = sys.argv[2] # Extract server IP
    server_port = sys.argv[4]  # Extract server port
    hash_block_size = sys.argv[6]  # Extract S
    file_path = sys.argv[8]  # Extract file path

    try:
        server_port = int(server_port)  # Extract server port from command line arguments
        #Also will check if the value matches what the pdf said and the maximum for a tcp port#
        if server_port < 1024 or server_port > 65535:
            raise Exception()
    except: #IF user did not give a vlid integer or gave a port too high or low
        sys.exit('Error, port# must be a valid integer (1024 < port# < 65,535)')
        
    try:
        hash_block_size = int(hash_block_size)  # Extract server port from command line arguments
        #Also will check if the value matches what the pdf said and the maximum for a tcp port#
    except: #IF user did not give a vlid integer or gave a port too high or low
        sys.exit('Error, hash block size must be a valid integer')
   
    # Open our file from command line
    try:
        chosen_file = open(file_path)
    except:
        sys.exit('File not found in directory, please make file before')

    # Connect to the server!
    server_socket = connect_server(server_ip, server_port)

    # Initialization Message Portion
    # Write your logic for initilization message
    
    initial_message = create_initialization(hash_block_size)
    server_socket.send(initial_message)

    print("Initialization sent.")

    # Acknowledgement Message Verification (write your code below)
    

    # Let's keep track of hash count, and our new hashed data file
    # you can write the hash values received from the server in this file
    hashed_file = open('hash_file.txt', 'w') #w will over right whatever was in that file
    print("New Hashed File Created.")
    ack = server_socket.recv(42) 
    print('Recieved Acknowledgement: ')
    server_block_size = check_acknowledgement(ack) # Get the total length of each response 
    #print(server_block_size)

    
    # Write your code to implement client's side protocol logic.

    #N  = 'something' #N is the total number of messages, which is hard to find so I will go with a different approach 
    #I gotta read from the file and while there are lines 
    #I will use a function to get all the messages and send the data like that
    to_send_arr = read_file(file_path, hash_block_size) # Now the information is in the array and split up by the block size

    #Now I will send each block by creating a struct and iterating over the list
    for i, payload in enumerate(to_send_arr):
        #Make the message
        message = create_hash_request(i,hash_block_size, payload.encode())
        server_socket.send(message)
        #After sending the message, a response is expected, with the size given by the ack
        hashed_message = server_socket.recv(42)
        _,_,_,hashed_data = open_struct(hashed_message)
        hashed_file.write(hashed_data.decode() + '\n')

    # We're done - Let's close our open files and sockets
    print("Done! Closing files and sockets.")
    # New Hash Data File
    hashed_file.close()
    # Command Line File
    chosen_file.close()
    # Server Socket
    server_socket.close()



