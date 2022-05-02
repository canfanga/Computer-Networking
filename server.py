from helper_functions import decode, header, readdirectory, findrecipe, checksum_calculator, packet_split
import socket
import struct
 

#localIP= "0.0.0.0"
localIP= "127.0.0.1"
localPort= 42069
bufferSize= 100 
directory_in_str= "recipe"
 

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
 
print("UDP server up and listening")
 

# Listen for incoming datagrams

while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        #CAL LLEGIR CADA TROÇ AMB LO DE ADALT ROLLO CADA ITEM OCUPA UN NUMERO GOOD

        udp_header = message[:16]
        data = message[16:]

        #decode tu mama
        decodedmessage = decode(message)
        client_message = decodedmessage[5].decode()

        if decodedmessage[1] == 1:  #user's message is hello
            packet = struct.pack("!i", bufferSize)
            hello_packet = header(0, 1, 1, 1, checksum_calculator(packet), packet)
            UDPServerSocket.sendto(hello_packet, address)

        if decodedmessage[1] == 2:  #user's message is id
            recipe_id = decodedmessage[1:]
            try:
                recipe = findrecipe(client_message, directory_in_str)
                separateMessage, number_parts = packet_split(bufferSize, recipe)
                
                if number_parts == 1:
                    packet = separateMessage[0].encode()
                    UDPServerSocket.sendto(header(decodedmessage[0],5,1,1,0,packet), address)

                else:
                    for x in range(number_parts):
                        packet = separateMessage[x].encode()
                        x = x + 1
                        UDPServerSocket.sendto(header(decodedmessage[0],5,number_parts,x,0,packet), address)
                        ackfromClient = UDPServerSocket.recvfrom(bufferSize)
                        decodedmessage = decode(ackfromClient[0])
                        ack_reply = decodedmessage[3] 
            except:
                #Send not found to client
                UDPServerSocket.sendto(header(0, 8, 1, 1, checksum_calculator(bytes()),bytes()), address)

        if decodedmessage[1] == 3:  #user's message is list
            #decode el packete enviat si es un empty string envia la full llista si es un empty string i si no pues envia namas los que contengan eso
            decodedmessage = decode(message)
            client_message = decodedmessage[5].decode()

            all_recipes = readdirectory(directory_in_str, client_message)
            packet = all_recipes.encode('UTF-8')
            UDPServerSocket.sendto(header(decodedmessage[0],4,1,1,0,packet), address)
            
        
        if decodedmessage[1] == 6: #user's message is goodbye
            adios_packet = header(0, 6, 1, 1, checksum_calculator(bytes()), bytes())
            UDPServerSocket.sendto(adios_packet, address)

        clientMsg = "Message from Client:{}".format(data)
        header_data = "Data from Header:{}".format(udp_header)
        clientIP  = "Client IP Address:{}".format(address[1])

        print(header_data)
        print(clientMsg)
        print(clientIP)
    except Exception as error:
        #Send error message to client
        packet = error.encode()
        UDPServerSocket.sendto(header(0, 7, 1, 1, checksum_calculator(packet),packet), address)
