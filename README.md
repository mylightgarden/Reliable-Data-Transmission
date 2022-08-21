# Reliable-Data-Transmission

This repo includes a python application of a reliable data transmission on top of an unreliable network channel.

**The application simulate many of the features of TCP and can:**

• Deliver all of the data, short or long, with no errors

• Succeed even with all of the unreliable features enabled ( see below for the unraliable features)

• Send multiple segments at a time (pipeline)

• Utilize a flow-control ‘window’

• Utilize cumulative ack

• Utilize selective retransmit

• Include segment ‘timeouts’ (use iteration count, not actual time)

• Abide by the payload size constant provided in the RDTLayer class

• Abide by the flow-control window size constant provided in the RDTLayer class

• Efficiently run with the fewest packets sent/received. 


 **The UnreliableChannel class may do any of the following:**
 
• Deliver packets out-of-order (data or ack packets)

• Delay packets by several iterations (data or ack packets)

• Drop packets (data or ack packets)

• Experience errors in transmission (failed checksum - data packets only)

• Various combinations of the above


### How to run: ###
Simply run: **py rtd_main.py**
