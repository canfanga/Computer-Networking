import math
import re
import struct
import os

#Check sum using Longitudinal redundancy check 
def checksum_calculator(packet):
    lrc = 0
    for b in packet:
        lrc = (lrc + b) & 0xFF
    return (((lrc ^ 0xFF) + 1) & 0xFF)

#Decode the message from the server
def decode(data:bytes):
    data1 = bytearray(data)
    header = data1[0:8]
    messageNumber = header[0]
    messageType = header[1]
    numberParts = header[2]
    progressMessage = header[3]
    checksum = header[4]
    data2 = bytes(data1[8:]) 
    return(messageNumber,messageType,numberParts,progressMessage,checksum,data2)

#Create a header
def header(message_number: int, message_type: int, number_parts: int, progress_message: int, checksum: int, packet: bytes):
    #Creating header with this structure UDP_header =  struct.pack(format, message_number, message_type, number_parts, progress_message, checksum, three 0's)

    message_number = message_number.to_bytes(1, "big")      #Contains the number of the message that is being send
    message_type = message_type.to_bytes(1, "big")          #Contains the type of the message that is being send
    number_parts = number_parts.to_bytes(1, "big")          #The number of packets that are necessary to be created for the message to be send on it’s entirety
    progress_message = progress_message.to_bytes(1, "big")  #Which part of the message does this package represent
    checksum = (0).to_bytes(1, "big")                       #Checksum using LRC

    UDP_header =  struct.pack("!cccccBBB", message_number, message_type, number_parts, progress_message, checksum,0,0,0)

    UDP_header_packet = bytearray(UDP_header + packet)

    checksum = checksum_calculator(UDP_header_packet)

    UDP_header_packet[4] = checksum

    #print(UDP_header_packet)

    return bytes(UDP_header_packet)

def readdirectory(directory_in_str, recipe_name):
    directory = os.fsencode(directory_in_str)
    final_string = ""
    if recipe_name == "":    #list was requested
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            filename = filename.replace("_"," ")
            filename = filename.replace(".txt","")
            filename = filename.replace("-"," ")
            filename= filename[0]+':'+filename[2:]
            final_string = final_string + filename  + "\n"
    else:
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if recipe_name in filename:
                filename = filename.replace("_"," ")
                filename = filename.replace(".txt","")
                filename = filename.replace("-"," ")
                filename= filename[0]+':'+filename[2:]
                final_string = final_string + filename  + "\n"

    return final_string

def findrecipe(id, directory_in_str):
    directory = os.fsencode(directory_in_str)
    receta = ""   
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(id):
            #print("no funciona")
            with open(os.path.join(directory_in_str, filename), "r") as f:
                receta = "".join(f.readlines())
    return receta

    #Check the number of packets necesary to be created to send the whole message and return number and splited msg
def packet_split(server_buffersize, clientMessage):
    if len(clientMessage.encode())<((server_buffersize)-8):
        return [clientMessage.encode()], 1
        
    division = math.ceil(len(clientMessage.encode()) / (server_buffersize-8))
    separateMessage = [0]*division

    a = server_buffersize-8 
    for x in range(division):
        separateMessage[x] = clientMessage[x*a:(x*a)+a]
    
    return separateMessage, len(separateMessage)