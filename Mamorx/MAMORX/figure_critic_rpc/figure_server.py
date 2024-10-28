from concurrent import futures 
from figure_critic import FigureCritic
from anthropic import AnthropicBedrock
import os
from dotenv import dotenv_values
import grpc
import figure_service_pb2
import figure_service_pb2_grpc
from PIL import Image

config = dotenv_values(".env")

class figureCriticServiceServicer(figure_service_pb2_grpc.figureCriticServiceServicer):
    def __init__(self):
        self.client = AnthropicBedrock(
            # getenv does not work at the current state
            # need alternative ways to manage the environment variables for the server
            aws_access_key= config['AWS_ACCESS_KEY_ID'],
            aws_secret_key= config['AWS_SECRET_ACCESS_KEY'],
            aws_region= config['AWS_DEFAULT_REGION'],
        )
        self.figure_critic = FigureCritic(client=self.client) 


    def SendPDF(self, request, context):
        try:
            pdf = request.pdf
            title = request.title
            abstract = request.abstract

            analysis = self.figure_critic.analyze_pdf(pdf_content=pdf, title=title, abstract=abstract)
            return figure_service_pb2.pdfResponse(response=analysis)
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return figure_service_pb2.pdfResponse(
                response=f"Error processing PDF: {str(e)}"
            )

        
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    figure_service_pb2_grpc.add_figureCriticServiceServicer_to_server(figureCriticServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()