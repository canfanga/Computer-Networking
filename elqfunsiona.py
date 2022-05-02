import math
import socket
import struct
from helper_functions import decode, header, checksum_calculator, packet_split

serverAddressPort= ("127.0.0.1", 42069)
#serverAddressPort= ("10.77.47.75", 42069)
bufferSize= 100
source_port = 1111

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#FUNCTIONS USED IN THE CODE

countMessages = 1 #set counter to 1

def askID():
    while True:
        try:
            idNumber = input("Insert the id of the recipe you want:")
            break
        except ValueError:
            print("Oops!  That was no valid number.  Try again...")
    return idNumber

#Checks what type of message and returns its numeric value associated
messageType= 0
def type_reader(outputClient):
    data = ""
    if outputClient == "C":
        adios_packet = header(0, 6, 1, 1, checksum_calculator(bytes()), bytes())
        UDPClientSocket.sendto(adios_packet, serverAddressPort)
            
        replyFromServer = UDPClientSocket.recvfrom(bufferSize)
        print("Goodbye")
        quit()
    elif outputClient == "id":
        messageType = 2
        data = askID()
    elif outputClient == "list":
        messageType = 3
    else:
        #ask client for the right thing
        print("Please insert a valid instruction. Remember that the program is case sensitive.")
        messageType = 7
    return (messageType, data)

#INICIO DEL PROTOCOLO NASHE
#SEND HELLO MESSAGE TO SERVER AND RECIVE EL SUYO
packet = struct.pack("!i", bufferSize)
countMessages = countMessages +1
hello_packet = header(countMessages, 1, 1, 1, checksum_calculator(packet), packet)
UDPClientSocket.sendto(hello_packet, serverAddressPort)

#Get message from server and print it
msgFromServer, _ = UDPClientSocket.recvfrom(bufferSize)
decodedmessage = decode(msgFromServer)
#server_hello = "Message from Server {}".format(decodedmessage[5])
#print(server_hello)

#upack server hello and get the buffer size :)
severbufferSize = struct.unpack("!i", decodedmessage[5])[0]

#funcion que conti el numero de parts per cada cop que s'envia un packet

while (True):
    outputUser = input("Welcome to the Simple Recipe Protocol, type C to leave the program or type id/list to choose your searching method:")

    #send the info to the server
    datalen = len(packet)
    order = 0
    bytesToSend= str.encode(outputUser)
    t, data = type_reader(outputUser)
    packet = data.encode()
    countMessages = countMessages +1
    output_packet = header(countMessages, t, packet_split(severbufferSize, data)[1], order, checksum_calculator(packet), packet)
    UDPClientSocket.sendto(output_packet, serverAddressPort)

    #Get message from server and print it
    replyFromServer = UDPClientSocket.recvfrom(bufferSize)
    decodedmessage = decode(replyFromServer[0])
    server_reply = decodedmessage[5].decode()

    #Error happened
    if decodedmessage[1]==7:
        #print error and re send hello message to server
        print(server_reply)
        hello_packet = header(countMessages, 1, 1, 1, checksum_calculator(packet), packet)
        UDPClientSocket.sendto(hello_packet, serverAddressPort)

    if decodedmessage[1] == 4:
        if decodedmessage[2] != decodedmessage[3]:
            #send ack to serv
            final_r = server_reply
            for x in range(decodedmessage[2]):
                #send ack to serv
                order = order + 1
                ack_packet = header(countMessages, 0, 1, order, checksum_calculator(bytes()), bytes())
                UDPClientSocket.sendto(ack_packet, serverAddressPort)

                if x != decodedmessage[2] - 1:
                    replyFromServer = UDPClientSocket.recvfrom(bufferSize)
                    decodedmessage = decode(replyFromServer[0])
                    server_reply = decodedmessage[5].decode()
                    final_r += server_reply
            print (final_r)
        else:
            print(server_reply)
        
        #send the request id to the server que NARISES
        t, data = type_reader("id")
        #splitted_message, order = find_prog(packet_split(severbufferSize, outputUser)[0], order)
        packet = data.encode()
        datalen = len(packet)
        bytesToSend= str.encode(outputUser)
        countMessages = countMessages +1
        output_packet = header(countMessages, t, packet_split(severbufferSize, outputUser)[1], order, checksum_calculator(packet), packet)
        UDPClientSocket.sendto(output_packet, serverAddressPort)
            
        replyFromServer = UDPClientSocket.recvfrom(bufferSize)
        decodedmessage = decode(replyFromServer[0])
        server_reply = decodedmessage[5].decode()

        #if que mira el decoded message si es igual [2]/[3] si lo es no mandes ack si es distino p
        if decodedmessage[2] != decodedmessage[3]:
            #send ack to serv
            final_r = server_reply
            for x in range(decodedmessage[2]):
                #send ack to serv
                order = order + 1
                ack_packet = header(countMessages, 0, 1, order, checksum_calculator(bytes()), bytes())
                UDPClientSocket.sendto(ack_packet, serverAddressPort)

                if x != decodedmessage[2] - 1:
                    replyFromServer = UDPClientSocket.recvfrom(bufferSize)
                    decodedmessage = decode(replyFromServer[0])
                    server_reply = decodedmessage[5].decode()
                    final_r += server_reply
            print (final_r)
        else:
            print(server_reply)
    #recipe not found :(

    if decodedmessage[1]== 8:
        print ("That id is not in the list. Please insent a valid id.")
               
    if decodedmessage[1] == 5:
        #if que mira el decoded message si es igual [2]/[3] si lo es no mandes ack si es distino 
        if decodedmessage[2] != decodedmessage[3]:
            #send ack to serv
            final_r=server_reply
            for x in range(decodedmessage[2]):

                order = order + 1
                ack_packet = header(countMessages, 0, 1, order, checksum_calculator(bytes()), bytes())
                UDPClientSocket.sendto(ack_packet, serverAddressPort)

                if x != decodedmessage[2] -1:
                    replyFromServer = UDPClientSocket.recvfrom(bufferSize)
                    decodedmessage = decode(replyFromServer[0])
                    server_reply = decodedmessage[5].decode()
                    final_r += server_reply
            print (final_r)
        else:
            print(server_reply)

        outputUser = input("Enjoy your recipe do you need anything else [Y/n]?")
        if outputUser == "Y":
            print("")
        if outputUser == "n":
            adios_packet = header(0, 6, 1, 1, checksum_calculator(bytes()), bytes())
            UDPClientSocket.sendto(adios_packet, serverAddressPort)
            
            replyFromServer = UDPClientSocket.recvfrom(bufferSize)
            print("Goodbye")
            quit()
    #else:
        #print("a estas alturas yo q se brodi")

