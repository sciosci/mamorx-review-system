import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import grpc
import logging

from concurrent import futures
from MAMORX.figure_critic_rpc import figure_critic_pb2
from MAMORX.figure_critic_rpc import figure_critic_pb2_grpc
from services.papermage_service.figure_critic_server import FigureCriticService

    
def serve():
    port = "5001"
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 20000000),
            ('grpc.max_receive_message_length', 20000000)
        ]
    )
    figure_critic_pb2_grpc.add_FigureCriticServiceServicer_to_server(FigureCriticService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()