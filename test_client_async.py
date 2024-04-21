import base64
import uuid
import zmq
from PIL import Image
import zmq
import json
import io
import io
import asyncio

# Generate a unique identifier
_rid = "{}".format(str(uuid.uuid4()))

# Prepare the ZeroMQ context and socket
context = zmq.Context()  # Create a ZeroMQ context
socket = context.socket(zmq.DEALER)  # Create a ZeroMQ DEALER socket
socket.setsockopt_string(zmq.IDENTITY, _rid)  # Set the socket identity to the unique identifier
socket.connect("tcp://localhost:5576")  # Connect the socket to the server

# Asynchronous function to send image data
async def test_zmq_embdserver(image_file_name):
    # Open and read the image file in binary mode
    with open(image_file_name, "rb") as image_file:
        img_str = base64.b64encode(image_file.read())  # Encode the image data in base64

    socket.send_json({"payload": img_str.decode("utf-8"), "_rid": _rid})  # Send image data as JSON
    msg = await asyncio.to_thread(socket.recv_string)  # Receive response
    data = json.loads(msg)  # Parse JSON response
    preds = data["preds"]  # Extract predictions from the received data
    print(preds)  # Print the predictions

    # Decode the image data and display the image
    image = Image.open(io.BytesIO(base64.b64decode(data["image"])))  # Decode and open the image
    image.show()  # Display the image

if __name__ == "__main__":
    name = "sample.png"  # Specify the name of the sample image file

    asyncio.run(test_zmq_embdserver(name))  # Run the asynchronous function to send image data

    # Close the socket and terminate the context
    socket.close()  # Close the ZeroMQ socket
    context.term()  # Terminate the ZeroMQ context