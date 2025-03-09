import socket
import struct
import time
import random
import csv

# Constants
TIMEOUT = 0.05  # 50ms timeout
CSV_FILENAME = "completion_times.csv"


class Sender:
    def __init__(self, receiver_ip, receiver_port, file_path, error_rate=0.0, loss_rate=0.0):
        self.receiver_addr = (receiver_ip, receiver_port)
        self.file_path = file_path
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.seq_num = 0
        self.error_rate = error_rate
        self.loss_rate = loss_rate

    @staticmethod
    def corrupt_ack(ack, error_rate):
        """Simulate ACK corruption by flipping a bit."""
        if random.random() < error_rate:
            return ack ^ 0b1  # Flip the least significant bit
        return ack

    def send_file(self):
        start_time = time.time()  # Start time measurement
        with open(self.file_path, 'rb') as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    # Send an empty packet as EOF signal
                    self.sock.sendto(struct.pack('!I', self.seq_num), self.receiver_addr)
                    break

                # Create packet with sequence number
                packet = struct.pack('!I', self.seq_num) + chunk
                self.sock.sendto(packet, self.receiver_addr)

                while True:
                    try:
                        ack_packet, _ = self.sock.recvfrom(4)

                        # Simulate ACK packet loss
                        if random.random() < self.loss_rate:
                            print("Simulating ACK loss. Dropping ACK.")
                            continue  # Skip processing this ACK

                        ack = struct.unpack('!I', ack_packet)[0]
                        ack = self.corrupt_ack(ack, self.error_rate)

                        if ack == self.seq_num:
                            self.seq_num ^= 1  # Flip sequence number
                            break
                    except socket.timeout:
                        print("Timeout! Resending packet...")
                        self.sock.sendto(packet, self.receiver_addr)

        end_time = time.time()  # End time measurement
        completion_time = end_time - start_time
        print(f"File transfer complete. Time taken: {completion_time:.3f} seconds.")

        # Log completion time
        with open(CSV_FILENAME, "a") as csv_append_file:
            csv_append_writer = csv.writer(csv_append_file)
            csv_append_writer.writerow([self.error_rate, self.loss_rate, completion_time])

        self.sock.close()


if __name__ == "__main__":
    # Clear CSV file before running
    with open(CSV_FILENAME, "w") as csv_init_file:
        csv_init_writer = csv.writer(csv_init_file)
        csv_init_writer.writerow(["Error Rate", "Loss Rate", "Completion Time (s)"])  # CSV Header

    for rate in [x / 100 for x in range(0, 65, 5)]:  # From 0.0 to 0.60 in 0.05 steps
        for scenario in range(1, 6):
            print(f"Running test with error/loss rate: {rate*100}% for Scenario {scenario}")

            # Initialize sender to be guaranteed defined before it's used
            sender = None  # Default initialization, ensuring sender is always defined

            if scenario == 1:
                # No errors or losses
                sender = Sender("127.0.0.1", 5001, "tiger.jpg", error_rate=0.0, loss_rate=0.0)
            elif scenario == 2:
                # ACK packet bit-error
                sender = Sender("127.0.0.1", 5001, "tiger.jpg", error_rate=rate, loss_rate=0.0)
            elif scenario == 3:
                # Data packet bit-error
                sender = Sender("127.0.0.1", 5001, "tiger.jpg", error_rate=0.0, loss_rate=0.0)
            elif scenario == 4:
                # ACK packet loss
                sender = Sender("127.0.0.1", 5001, "tiger.jpg", error_rate=0.0, loss_rate=rate)
            elif scenario == 5:
                # Data packet loss
                sender = Sender("127.0.0.1", 5001, "tiger.jpg", error_rate=0.0, loss_rate=rate)

            if sender:  # Only call send_file() if sender is defined
                sender.send_file()
