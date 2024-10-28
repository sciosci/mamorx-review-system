# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import MAMORX.figure_critic_rpc.figure_critic_pb2 as figure__critic__pb2


class FigureCriticStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Hello = channel.unary_unary(
                '/FigureCritic.FigureCritic/Hello',
                request_serializer=figure__critic__pb2.helloMsg.SerializeToString,
                response_deserializer=figure__critic__pb2.helloReply.FromString,
                )


class FigureCriticServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Hello(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FigureCriticServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Hello': grpc.unary_unary_rpc_method_handler(
                    servicer.Hello,
                    request_deserializer=figure__critic__pb2.helloMsg.FromString,
                    response_serializer=figure__critic__pb2.helloReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'FigureCritic.FigureCritic', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FigureCritic(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Hello(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/FigureCritic.FigureCritic/Hello',
            figure__critic__pb2.helloMsg.SerializeToString,
            figure__critic__pb2.helloReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
