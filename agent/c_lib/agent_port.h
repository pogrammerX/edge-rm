#ifndef AGENT_PORT_H
#define AGENT_PORT_H

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

typedef void (*agent_port_timer_cb)(); 
typedef void (*agent_port_coap_receive_cb)(uint8_t, uint8_t*, uint32_t); 

//Resources
float agent_port_get_free_memory();
float agent_port_get_free_cpu();
const char* agent_port_get_agent_id();
const char* agent_port_get_agent_name();
const char* agent_port_get_os();

//Timing
void agent_port_start_timer_repeated(uint32_t timer_rate_ms, agent_port_timer_cb cb);
void agent_port_stop_timer_repeated();

//COAP
void agent_port_register_coap_receive_cb(agent_port_coap_receive_cb cb);
void agent_port_coap_send(const char* destination, uint8_t* payload, uint32_t len);

//Utilities
void agent_port_print(const char* fmt, ...);

//memory
void* agent_port_malloc(size_t size);
void agent_port_free(void* pt);

//devices
typedef struct _agent_device_t {
    char* name;
    char* reference;
} agent_device_t;

bool agent_port_get_device(uint8_t device_number, agent_device_t* device);

#endif
