import figure_service_pb2
import figure_service_pb2_grpc
import time
import grpc
import base64
import sys

def do_figure_critic(stub, debug=False):
    pdf = open("test.pdf", "rb").read()
    test_title = "Modeling Content and Context with Deep Relational Learning"
    test_abstract = """
    Building models for realistic natural language tasks requires dealing with long texts and accounting for complicated structural dependencies. 
    Neural-symbolic representations have emerged as a way to combine the reasoning capabilities of symbolic methods, with the
    expressiveness of neural networks. However,most of the existing frameworks for combining neural and symbolic representations have been
    designed for classic relational learning tasks that work over a universe of symbolic entities and relations. In this paper, we present DRAIL,
    an open-source declarative framework for specifying deep relational models, designed to support a variety of NLP scenarios. Our frame-
    work supports easy integration with expressive language encoders, and provides an interface to study the interactions between representation,
    inference and learning.
    """
    request = figure_service_pb2.sendPDFMsg(pdf=pdf, title=test_title, abstract=test_abstract)
    response = stub.SendPDF(request)
    if debug:
        print(response.response)
    return response

def run(host, cmd, debug=False):
    with grpc.insecure_channel(f"{host}:50051") as channel:
        stub = figure_service_pb2_grpc.figureCriticServiceStub(channel)
        
        
        start = time.perf_counter()
        if cmd == 'figureCritic':
                do_figure_critic(stub, debug)
        else:
            print("Unknown option", cmd)
            return
        
        delta = ((time.perf_counter() - start))*1000
        print("Took", delta, "ms for this operation")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <server ip> <cmd> ")
        print(f"where <cmd> is 'figureCritic'")
        sys.exit(1)

    host = sys.argv[1]
    cmd = sys.argv[2]
    
    run(host, cmd, debug=True)