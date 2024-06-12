# File path: pytorch_image_classification_server.py

from io import BytesIO
from PIL import Image
import threading
import zmq
from base64 import b64decode, b64encode
import numpy as np
import torch
from torchvision import transforms
import timm
import json
import os
import io


# Load model using timm
model_name = "mobilenetv2_100"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = timm.create_model(model_name, pretrained=True)
model.eval()
model.to(device)

# Define image preprocessing
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # Standard ImageNet mean
        std=[0.229, 0.224, 0.225]    # Standard ImageNet std
    ),
])

# Get class labels
with open('imagenet_classes.json') as f:
    class_labels = json.load(f)

class Server(threading.Thread):
    def __init__(self):
        self._stop = threading.Event()
        threading.Thread.__init__(self)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("tcp://*:5576")

        backend = context.socket(zmq.DEALER)
        backend.bind("inproc://backend_endpoint")

        poll = zmq.Poller()
        poll.register(frontend, zmq.POLLIN)
        poll.register(backend, zmq.POLLIN)

        while not self.stopped():
            sockets = dict(poll.poll())
            if frontend in sockets:
                if sockets[frontend] == zmq.POLLIN:
                    _id = frontend.recv()
                    json_msg = frontend.recv_json()

                    handler = RequestHandler(context, _id, json_msg)
                    handler.start()

            if backend in sockets:
                if sockets[backend] == zmq.POLLIN:
                    _id = backend.recv()
                    msg = backend.recv()
                    frontend.send(_id, zmq.SNDMORE)
                    frontend.send(msg)

        frontend.close()
        backend.close()
        context.term()

class RequestHandler(threading.Thread):
    def __init__(self, context, id, msg):
        threading.Thread.__init__(self)
        self.context = context
        self.msg = msg
        self._id = id
        self.buffered = io.BytesIO()
        self.image_data = None

    def process(self, obj):
        imgstr = obj["payload"]
        img_original = Image.open(BytesIO(b64decode(imgstr)))
        img = img_original.convert("RGB")

        img_tensor = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        top_prob, top_catid = torch.topk(probabilities, 3)
        preds = [
            f"{class_labels[str(catid.item())]}: {prob.item():.5f}"
            for prob, catid in zip(top_prob, top_catid)
        ]

        # Convert processed image to base64
        img_original.save(self.buffered, format="JPEG")
        self.image_data = b64encode(self.buffered.getvalue()).decode("utf-8")

        return {
            "preds": ", ".join(preds),
            "image": self.image_data,
        }

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect("inproc://backend_endpoint")

        output = self.process(self.msg)

        worker.send(self._id, zmq.SNDMORE)
        worker.send_string(json.dumps(output))

        worker.close()

def main():
    server = Server()
    server.start()

if __name__ == "__main__":
    main()
