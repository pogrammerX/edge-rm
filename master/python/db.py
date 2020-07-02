import messages_pb2
import threading

agents = {}
id_counter = 0

class AtomicCounter:
    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.value = initial
        self._lock = threading.Lock()

    def increment(self, num=1):
        """Atomically increment the counter by num (default 1) and return the
        new value.
        """
        with self._lock:
            self.value += num
            return self.value
agent_counter = AtomicCounter()
offer_counter = AtomicCounter()

def get_offer_id():
	return offer_counter.increment()

def add_agent(resources, attributes):
	aid = agent_counter.increment()
	while aid in agents:
		aid = agent_counter.increment()
	agents[aid] = {
		"id":aid,
		"resources":resources,
		"attributes":attributes
	}
	return aid

def get_all_agents():
	return agents.values()

def get_agent(agent_id):
	return agents[agent_id]

def delete_agent(agent_id):
	if agent_id in agents:
		del agents[agent_id]