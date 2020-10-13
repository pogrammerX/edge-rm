#!/usr/bin/env python3

import argparse
import getopt
import time
import sys
import threading

import flask
app = flask.Flask(__name__)

sys.path.insert(1, '../../support/CoAPthon3')
from coapthon.server.coap import CoAP
from coapthon import defines
from coapthon.resources.resource import Resource

import messages_pb2

import db

# TODO + NOTES:
# Issue: What if the agent never pings to receive their task?
# Issue: How do we ensure that the agent successfully started the task we assigned them?
# Todo: De-register agent when they dont ping for a while
# Todo: Keep track of available resources

class BasicResource(Resource):
    def __init__(self, name="BasicResource", coap_server=None):
        super(BasicResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Hello World"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.edit_resource(request)
        return self

    def render_POST(self, request):
        print(request);
        res = self.init_resource(request, BasicResource())
        return res

    def render_DELETE(self, request):
        return True

class RequestOfferResource(Resource):
    def __init__(self, name="RequestResource", coap_server=None):
        super(RequestOfferResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Test"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_POST_advanced(self, request, response):
        wrapper = messages_pb2.WrapperMessage()
        try:
            wrapper.ParseFromString(request.payload)
        except:
            print("Error parsing protobuf - not responding.")
            response.code = defines.Codes.BAD_REQUEST.number
            return self, response

        framework_id = wrapper.request.framework_id

        #first, clear any agents that have dropped off
        db.clear_stale_agents()

        #construct resource offer subtracting the resources of any tasks in the task queue
        print("\nGot resource offer request! Framework \"" + framework_id + "\"\n")

        #currently just giving the framework everything we got
        wrapper = messages_pb2.WrapperMessage()
        wrapper.type = messages_pb2.WrapperMessage.Type.RESOURCE_OFFER
        wrapper.offermsg.framework_id = framework_id
        for agent in db.get_all_agents():
            offer = wrapper.offermsg.offers.add()
            offer.id = db.get_offer_id()
            offer.framework_id = framework_id
            offer.agent_id = agent.id
            offer.attributes.extend(agent.attributes)
            
            offer.resources.extend(agent.resources)

            #get pending tasks for agent to subract pending resources
            pending = db.get_all_pending_tasks_by_agent(agent.id)

            #currently only do this for scalars
            for resource in offer.resources:
                for task in pending:
                    for tresource in task.resources:
                        if resource.name == tresource.name:
                            if resource.scalar.value and tresource.scalar.value:
                                resource.scalar.value -= tresource.scalar.value

        response.payload = wrapper.SerializeToString()
        response.code = defines.Codes.CHANGED.number
        response.content_type = defines.Content_types["application/octet-stream"]
        return self, response

class RunTaskResource(Resource):
    def __init__(self, name="RunTaskResource", coap_server=None):
        super(RunTaskResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Test"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_POST_advanced(self, request, response):
        print("Received Task Request!")

        # unpack request
        wrapper = messages_pb2.WrapperMessage()
        try:
            wrapper.ParseFromString(request.payload)
        except:
            print("Error parsing protobuf - not responding.")
            response.code = defines.Codes.BAD_REQUEST.number
            return self, response

        # print request (do nothing right now)
        print("    Framework Name: " + wrapper.run_task.task.framework.name)
        print("    Framework ID:   " + wrapper.run_task.task.framework.framework_id)
        print("    Task Name:      " + wrapper.run_task.task.name)
        print("    Task ID:        " + wrapper.run_task.task.task_id)
        print("    Selected Agent: " + wrapper.run_task.task.agent_id)
        for i in range(len(wrapper.run_task.task.resources)):
            resource = wrapper.run_task.task.resources[i]
            print("        Resource: (" + resource.name + ") type: " + str(resource.type) + " amt: " + str(resource.scalar).strip())

        # TODO: Forward the request onto the particular device through a ping/pong
        db.add_task(wrapper.run_task)

        # construct response
        wrapper = messages_pb2.WrapperMessage()
        wrapper.type = messages_pb2.WrapperMessage.Type.PONG
        wrapper.pong.agent_id = wrapper.run_task.task.agent_id
        response.payload = wrapper.SerializeToString()
        response.code = defines.Codes.CHANGED.number
        response.content_type = defines.Content_types["application/octet-stream"]
        return self, response

class KillTaskResource(Resource):
    def __init__(self, name="KillTaskResource", coap_server=None):
        super(KillTaskResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Test"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_POST_advanced(self, request, response):
        print("Received Kill Task!")

        # unpack request
        wrapper = messages_pb2.WrapperMessage()
        try:
            wrapper.ParseFromString(request.payload)
        except:
            print("Error parsing protobuf - not responding.")
            response.code = defines.Codes.BAD_REQUEST.number
            return self, response

        # print request (do nothing right now)
        print("    Framework Name: " + wrapper.kill_task.framework.name)
        print("    Framework ID:   " + wrapper.kill_task.framework.framework_id)
        print("    Task Name:      " + wrapper.kill_task.name)
        print("    Task ID:        " + wrapper.kill_task.task_id)
        print("    Selected Agent: " + wrapper.kill_task.agent_id)

        # TODO: Forward the request onto the particular device through a ping/pong
        db.add_kill_task(wrapper.kill_task)

        # construct response
        wrapper = messages_pb2.WrapperMessage()
        wrapper.type = messages_pb2.WrapperMessage.Type.PONG
        wrapper.pong.agent_id = wrapper.kill_task.agent_id
        response.payload = wrapper.SerializeToString()
        response.code = defines.Codes.CHANGED.number
        response.content_type = defines.Content_types["application/octet-stream"]
        return self, response


class PingResource(Resource):
    def __init__(self, name="PingResource", coap_server=None):
        super(PingResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Hello World"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_POST_advanced(self, request, response):
        #unpack request
        
        print("Recevied ping request: " + str(request))

        wrapper = messages_pb2.WrapperMessage()

        try:
            wrapper.ParseFromString(request.payload)
        except:
            print("Error parsing protobuf - not responding.")
            response.code = defines.Codes.BAD_REQUEST.number
            return self, response

        agent_id = wrapper.ping.agent.id
        agent_name = wrapper.ping.agent.name
        if not agent_id:
            return self
        print("Ping! Agent ID:(" + str(agent_id) + ") Name:(" + str(agent_name) + ")")

        #refresh the agent timing
        db.refresh_agent(agent_id, wrapper.ping.agent)

        #update the state of any tasks it may have sent
        db.refresh_tasks(wrapper.ping.tasks)

        task_to_run = db.get_next_unissued_task_by_agent(agent_id)
        task_to_kill = db.get_next_unissued_kill_by_agent(agent_id)

        # construct response
        wrapper = messages_pb2.WrapperMessage()
        wrapper.type = messages_pb2.WrapperMessage.Type.PONG
        wrapper.pong.agent_id = str(agent_id)
        if task_to_run:
            print("Got a task to schedule!!!")
            wrapper.pong.run_task.task.CopyFrom(task_to_run)
        if task_to_kill:
            print("Got a task to kill!")
            wrapper.pong.kill_task.CopyFrom(task_to_kill)
        response.payload = wrapper.SerializeToString()
        response.code = defines.Codes.CONTENT.number
        # response.code = defines.Codes.CHANGED.number
        response.content_type = defines.Content_types["application/octet-stream"]
        return self, response

class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, (host, port), multicast)
        self.add_resource('basic/', BasicResource())
        # self.add_resource('register/', RegisterResource())
        self.add_resource('request/', RequestOfferResource())
        self.add_resource('task/', RunTaskResource())
        self.add_resource('kill/', KillTaskResource())
        self.add_resource('ping/', PingResource())

        print ("CoAP Server start on " + host + ":" + str(port))
        print (self.root.dump())

def start_coap_server(ip, port):  # pragma: no cover
    multicast = False
    server = CoAPServer(ip, int(port), multicast)
    try:
        server.listen(10)
    except:
        print("Server Shutdown")
        server.close()
        print("Exiting...")


### This section is responsible for the api server
@app.route('/agents', methods=['GET'])
@app.route('/', methods=['GET'])
def get_agents():
    return flask.jsonify(list(db.get_all_agents_as_dict()))

@app.route('/frameworks', methods=['GET'])
def get_frameworks():
    return flask.jsonify(list(db.get_all_frameworks_as_dict()))

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return flask.jsonify(list(db.get_all_tasks_as_dict()))

def start_api_server(host, port):
    app.run(host=host,port=port)


if __name__ == "__main__":  # pragma: no cover
    # if sys.version_info[0] >= 3:
    #     raise Exception("Must be using Python 2 (yeah...)")
    parser = argparse.ArgumentParser(description='Launch the CoAP Resource Manager Master')
    parser.add_argument('--host', required=True, help='the LAN IP to bind to.')
    parser.add_argument('--port', required=False, default=5683, help='the local machine port to bind to.')
    parser.add_argument('--api-port', required=False, default=8080, help='the local machine port to bind to.')
    args = parser.parse_args()

    #start API server in a thread
    api_server_thread = threading.Thread(target=start_api_server,args=(args.host,args.api_port,), daemon = True)
    api_server_thread.start()

    #start coap server
    start_coap_server(args.host, args.port)
