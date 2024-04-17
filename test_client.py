import base64
import uuid
import zmq
import matplotlib.pylab as plt
from PIL import Image
import zmq
from base64 import b64decode, b64encode
import json
import io


def test_zmq_embdserver(image_file_name):
    _rid = "{}".format(str(uuid.uuid4()))

    global img_str

    with open(image_file_name, "rb") as image_file:
        img_str = base64.b64encode(image_file.read())

    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.setsockopt_string(zmq.IDENTITY, _rid)
    socket.connect("tcp://localhost:5576")
    print("Client %s started\n" % _rid)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    obj = socket.send_json({"payload": img_str.decode("utf-8"), "_rid": _rid})

    received_reply = False
    while not received_reply:
        sockets = dict(poll.poll(1000))
        if socket in sockets:
            if sockets[socket] == zmq.POLLIN:
                msg = socket.recv_string()
                data = json.loads(msg)
                preds = data["preds"]
                print(preds)
                # Handling the Image
                image_data = base64.b64decode(data["image"])
                image = Image.open(io.BytesIO(image_data))
                image.show()
                del msg
                received_reply = True

    socket.close()
    context.term()


if __name__ == "__main__":
    name = "sample.png"
    test_zmq_embdserver(name)
