'''
Author:  Sophie Zhao
Sources used: TCP window size: https://www.youtube.com/watch?v=1zmaFD7Jb9c
https://www.d.umn.edu/~gshute/net/reliable-data-transfer.xhtml#:~:text=For%20connection%2Doriented%20service%20provided,designed%20using%20some%20basic%20tools
TCP Reliability, Flow Control, and Connection Management: https://www.youtube.com/watch?v=UYJP-6mhF6E
'''
from segment import Segment
import copy

# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #

class RDTLayer(object):
    # Class Scope Variables                                                                                            

    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed
    dataReceived = ''
    lastAckNum = 0
    lastSequenceNum = -1
    appendedSeqNum = []
    countSegmentTimeouts = 0

    # __init__()                                                                                                       
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        self.dataReceived = ''
        self.lastAckNum = 0
        self.lastSequenceNum = -1
        self.lastAckedSequenceNum = -1
        countSegmentTimeouts = 0   
        self.sentButNotAcked = []
        self.receivedNotDelivered = []
        self.seqnum = 0
        self.acknum = 0
                                                                                    
    # Description:                                                                                                     
    # Called by main to set the unreliable sending lower-layer channel
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # Description:                                                                                                    
    # Called by main to set the unreliable receiving lower-layer channel
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel
                                                                                                                 
    # Description:                                                                                                     
    # Called by main to set the string data to send                                                                    
    def setDataToSend(self,data):
        self.dataToSend = data
                                                                                                                 
    # Description:                                                                                                     
    # Called by main to get the currently received and buffered string data, in order
    def getDataReceived(self):        
        # Identify the data that has been received...
        # print('getDataReceived(): Complete this...')
        return self.dataReceived
    
    # Description:                                                                                                     
    # "timeslice". Called by main once per iteration
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()
                                                                                                               
    # Description:                                                                                                     
    # Manages Segment sending tasks
    def processSend(self): 
        # Go through the list of segments that have been sent by not yet acknowledged, and resend if timeout.
        for curr_seg in self.sentButNotAcked:
            # If timeout
            if (self.currentIteration - curr_seg.getStartIteration() > 4):                
                self.countSegmentTimeouts += 1               
                curr_seg.setStartIteration(self.currentIteration)
                #resend
                self.sendChannel.send(copy.copy(curr_seg))

       
        # The last data (the sequence number + data length) shoule be in the window size
        while ((self.seqnum + self.DATA_LENGTH) < (self.acknum + self.FLOW_CONTROL_WIN_SIZE)):

            if (len(self.dataToSend) > self.seqnum):                
                segmentSend = Segment()
                
                # Set start iteration 
                segmentSend.setStartIteration(self.currentIteration)
                
                # Set seq num and data
                data = self.dataToSend[self.seqnum:(self.seqnum+self.DATA_LENGTH)]
                segmentSend.setData(self.seqnum, data)
                self.sendChannel.send(copy.copy(segmentSend))                
                
                # Update Sequence number                
                self.seqnum = self.seqnum + self.DATA_LENGTH;
                
                # Add the segment to the sent but not acknowledged list
                self.sentButNotAcked.append(segmentSend)
                
            else:
                #All data are sent
                break


    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #

    def processReceiveAndSendRespond(self):
        segmentAck = Segment()                  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()
        
        to_ack = False
        for incoming_seg in listIncomingSegments:
            
            # When the incoming segment is an Ack
            # Default segment sequence is -1, if the segment is an ack segment, the sequence number remains -1.    
            if (incoming_seg.seqnum == -1): 
                # Because we utilize cumulative ack, all fragment having a sequence number that is smaller than acknum can be 
                #  considered as acknowledged and removed from sentButNotAcked list               
                self.sentButNotAcked[:] = [curr_seg for curr_seg in self.sentButNotAcked if not (curr_seg.seqnum < incoming_seg.acknum)]                
                self.acknum = incoming_seg.acknum
                to_ack = False 
                
            # If the packet is expected
            elif (incoming_seg.seqnum == self.acknum):
                # Check checksum
                if (incoming_seg.checkChecksum()):
                    self.dataReceived = self.dataReceived + incoming_seg.payload
                    self.acknum = self.acknum + self.DATA_LENGTH
                    
                    # We should check if there are additional segments we received out of order
                    for curr_seg in self.receivedNotDelivered:
                        if (self.acknum == curr_seg.seqnum): 
                            
                            self.acknum = self.acknum + self.DATA_LENGTH 
                            self.receivedNotDelivered.remove(curr_seg)
                            
                            self.dataReceived += curr_seg.payload                    

                    to_ack = True           
                       
            # If the packet after the expected pakcet arrives before the expected packet
            elif (incoming_seg.seqnum > self.acknum):
                # check and see if this sequence is already in the list
                if (incoming_seg.checkChecksum()):
                    if(not any(curr_seg.seqnum == incoming_seg.seqnum for curr_seg in self.receivedNotDelivered)):
                        self.receivedNotDelivered.append(incoming_seg)
                    to_ack = True
            else:
                to_ack = True

        # Acknowledge an incoming data segment, if needed
        if (to_ack):
            segmentAck = Segment()           
            # Display response segment
            segmentAck.setAck(self.acknum)
            print("Sending ack: ", segmentAck.to_string())

            # Use the unreliable sendChannel to send the ack packet
            self.sendChannel.send(segmentAck)
    
            
        
