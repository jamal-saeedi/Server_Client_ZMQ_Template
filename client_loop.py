import base64
import uuid
import zmq
import matplotlib.pylab as plt
from PIL import Image
import zmq
import json
import io

# Generate a unique ID for the client
_rid = "{}".format(str(uuid.uuid4()))

# Initialize ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.DEALER)
socket.setsockopt_string(zmq.IDENTITY, _rid)
socket.connect("tcp://localhost:5576")
print("Client %s started\n" % _rid)

# Initialize a poller for the socket
poll = zmq.Poller()
poll.register(socket, zmq.POLLIN)

# Define a function to test the ZeroMQ embedded server
def test_zmq_embdserver(image_file_name):
    # Open and read the image file in binary mode
    with open(image_file_name, "rb") as image_file:
        img_str = base64.b64encode(image_file.read())

    # Send the image data and unique ID to the server as JSON
    socket.send_json({"payload": img_str.decode("utf-8"), "_rid": _rid})

    received_reply = False
    # Wait for a reply from the server
    while not received_reply:
        # Poll the socket for incoming messages
        sockets = dict(poll.poll(1000))
        if socket in sockets:
            if sockets[socket] == zmq.POLLIN:
                # Receive and decode the message from the server
                msg = socket.recv_string()
                data = json.loads(msg)
                preds = data["preds"]  # Extract predictions from the received data
                print(preds)  # Print the predictions
                # Decode the image data and display the image
                image = Image.open(io.BytesIO(base64.b64decode(data["image"])))
                image.show()
                received_reply = True  # Set the flag to indicate that a reply has been received

# Entry point of the script
if __name__ == "__main__":
    name = "sample.png"  # Specify the name of the sample image file
    test_zmq_embdserver(name)  # Call the test function with the sample image file
    socket.close()  # Close the socket connection
    context.term()  # Terminate the ZeroMQ context