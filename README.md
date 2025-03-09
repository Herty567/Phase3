# Phase3
Team members: Jacob Alicea, Josiah Concepcion, Jamie Oliphant, Tim Saari

Name of files: receiver.py, sender.py, and tiger.jpg

A lot of the same functions from Phase 2 with a newly added countdown timer and an RDT 3.0 receiver/sender

The purpose of the receiver file is to listen for incomping packets from the sender file. Will validate packets checks for correct sequence of numbers to make sure there's no dupiclates. Will validate packets and write data to a new file 'received_tiger.jpg'.

The purpose of the sender file is to read the 'tiger.jpg' in 1024 byte chunks and create packets. Then it will send the packets to the receiver after sequencing them.

The purpose of the tiger.jpg is a 1.1 MB jpeg file to send through the transfer protocol. Its meant to test if the protocol works and can show if there was any packet loss or corruption.

The language used for this was Python and the compiler was PyCharm. Any Python environement that allows for two Python files to run at once should be able to run this protocol.

To compile the code you have to copy and paste the files in this Github into your complier environment. Then you run the receiver.py first so that it can wait for the sender.py to start running. Once you have the sender.py running the code will start going through the 5 different scenarios and record them in a seperate csv file. This file can then be used to make plots for each scenario at ease. This will take about 10+ minutes to get all the data into the csv file.
