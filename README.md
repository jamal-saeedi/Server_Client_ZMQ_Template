# Model Inference API with ZeroMQ

This repository offers a robust solution for interacting with a model inference API using ZeroMQ (ZMQ). With support for popular machine learning frameworks such as PyTorch and TensorFlow, it provides versatility for various project requirements.

## Features:

- **ZeroMQ Integration**: Seamlessly communicate with the model inference API using ZeroMQ, ensuring efficient and reliable message passing.

- **Framework Support**: Choose between PyTorch and TensorFlow for model inference, catering to diverse machine learning workflows.

- **Asynchronous Communication**: Opt for asynchronous communication to enhance responsiveness and handle multiple requests concurrently.

- **Continuous Interaction**: Utilize a while loop for continuous interaction with the API, ensuring smooth and uninterrupted data flow between the client and server.

## Getting Started:

1. **Installation**: Clone the repository and install the required dependencies using `pip`.

    ```bash
    git clone https://github.com/jamal-saeedi/zmq-inference-server-client-pytorch-tf
    cd zmq-inference-server-client-pytorch-tf
    pip install -r requirements.txt
    ```

2. **Usage**: Start by initializing the server and connecting the client to begin communicating with the model inference API.

    ```python
    # Start the server
    python inference_server_torch.py or inference_server_tf.py

    # Connect the client
    python client_async.py or client_loop.py
    ```
    

3. **Customization**: Customize the code to fit your specific use case, such as integrating custom models or extending functionality as needed.

## Contributing:

Contributions are welcome! Feel free to open issues for bug fixes, feature requests, or submit pull requests to enhance the repository's functionality.

## License:

This project is licensed under the MIT License

---

Feel free to adjust or expand upon this template based on your specific project requirements!

