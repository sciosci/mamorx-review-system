import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import grpc
import logging

from concurrent import futures
from MAMORX.figure_critic_rpc import figure_critic_pb2
from MAMORX.figure_critic_rpc import figure_critic_pb2_grpc
import os


class FigureCriticService(figure_critic_pb2_grpc.FigureCriticServicer):
    def Hello(self, request, context):
        return figure_critic_pb2.helloReply(msg=(request))
    

def serve():
    print(os.environ["API_KEY"])
    port = "5001"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    figure_critic_pb2_grpc.add_FigureCriticServicer_to_server(FigureCriticService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()