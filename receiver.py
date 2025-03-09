import socket
import struct
import random


class Receiver:
    def __init__(self, port, output_file, error_rate=0.0, loss_rate=0.0):
        self.port = port
        self.output_file = output_file
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", port))
        self.expected_seq = 0
        self.error_rate = error_rate
        self.loss_rate = loss_rate

    @staticmethod
    def corrupt_data(data, error_rate):
        """Simulate data corruption by flipping a bit."""
        if random.random() < error_rate:
            corrupted_data = bytearray(data)
            corrupted_data[0] ^= 0b1  # Flip a bit in the first byte
            return bytes(corrupted_data)
        return data

    def receive_file(self):
        with open(self.output_file, 'wb') as f:
            while True:
                packet, sender_addr = self.sock.recvfrom(1028)

                # Simulate packet loss (data packets)
                if random.random() < self.loss_rate:
                    print("Simulating data packet loss. Dropping packet.")
                    continue

                if len(packet) == 4:  # Only sequence number, means EOF
                    print("EOF received. Closing connection.")
                    break

                seq_num = struct.unpack('!I', packet[:4])[0]
                data = self.corrupt_data(packet[4:], self.error_rate)

                if seq_num == self.expected_seq:
                    f.write(data)
                    self.expected_seq ^= 1  # Flip sequence number

                # Simulate ACK packet loss
                if random.random() < self.loss_rate:
                    print("Simulating ACK packet loss. Dropping ACK.")
                    continue  # Simulate ACK packet loss

                # Send ACK with the expected sequence number (ACK for the next sequence)
                ack_packet = struct.pack('!I', self.expected_seq ^ 1)
                self.sock.sendto(ack_packet, sender_addr)

        print("File received successfully.")
        self.sock.close()


if __name__ == "__main__":
    for rate in [x / 100 for x in range(0, 65, 5)]:  # From 0.0 to 0.60 in 0.05 steps
        for scenario in range(1, 6):
            print(f"Running test with error/loss rate: {rate*100}% for Scenario {scenario}")

            # Initialize receiver for different scenarios
            receiver = None  # Default initialization, ensuring receiver is always defined

            if scenario == 1:
                # No errors or losses
                receiver = Receiver(5001, "received_tiger.jpg", error_rate=0.0, loss_rate=0.0)
            elif scenario == 2:
                # ACK packet bit-error
                receiver = Receiver(5001, "received_tiger.jpg", error_rate=rate, loss_rate=0.0)
            elif scenario == 3:
                # Data packet bit-error
                receiver = Receiver(5001, "received_tiger.jpg", error_rate=rate, loss_rate=0.0)
            elif scenario == 4:
                # ACK packet loss
                receiver = Receiver(5001, "received_tiger.jpg", error_rate=0.0, loss_rate=rate)
            elif scenario == 5:
                # Data packet loss
                receiver = Receiver(5001, "received_tiger.jpg", error_rate=0.0, loss_rate=rate)

            if receiver:  # Only call receive_file() if receiver is defined
                receiver.receive_file()
