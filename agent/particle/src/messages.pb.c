/* Automatically generated nanopb constant definitions */
/* Generated by nanopb-0.4.3 */

#include "messages.pb.h"
#if PB_PROTO_HEADER_VERSION != 40
#error Regenerate this file with the current version of nanopb generator.
#endif

PB_BIND(WrapperMessage, WrapperMessage, 2)


PB_BIND(PingAgentMessage, PingAgentMessage, AUTO)


PB_BIND(PongAgentMessage, PongAgentMessage, 2)


PB_BIND(AgentInfo, AgentInfo, AUTO)


PB_BIND(Resource, Resource, AUTO)


PB_BIND(Attribute, Attribute, AUTO)


PB_BIND(Value, Value, AUTO)


PB_BIND(Value_Scalar, Value_Scalar, AUTO)


PB_BIND(Value_Range, Value_Range, AUTO)


PB_BIND(Value_Ranges, Value_Ranges, AUTO)


PB_BIND(Value_Set, Value_Set, AUTO)


PB_BIND(Value_Text, Value_Text, AUTO)


PB_BIND(Value_Device, Value_Device, AUTO)


PB_BIND(ContainerInfo, ContainerInfo, AUTO)


PB_BIND(ContainerInfo_DockerInfo, ContainerInfo_DockerInfo, AUTO)


PB_BIND(ContainerInfo_DockerInfo_PortMapping, ContainerInfo_DockerInfo_PortMapping, AUTO)


PB_BIND(ContainerInfo_WASMInfo, ContainerInfo_WASMInfo, AUTO)


PB_BIND(ContainerInfo_WASMInfo_EnvironmentVariable, ContainerInfo_WASMInfo_EnvironmentVariable, AUTO)


PB_BIND(FrameworkInfo, FrameworkInfo, AUTO)


PB_BIND(TaskInfo, TaskInfo, AUTO)


PB_BIND(RunTaskMessage, RunTaskMessage, AUTO)


PB_BIND(KillTaskMessage, KillTaskMessage, AUTO)


PB_BIND(ResourceRequestMessage, ResourceRequestMessage, AUTO)


PB_BIND(ResourceOfferMessage, ResourceOfferMessage, AUTO)


PB_BIND(Offer, Offer, AUTO)


PB_BIND(OfferID, OfferID, AUTO)








#ifndef PB_CONVERT_DOUBLE_FLOAT
/* On some platforms (such as AVR), double is really float.
 * To be able to encode/decode double on these platforms, you need.
 * to define PB_CONVERT_DOUBLE_FLOAT in pb.h or compiler command line.
 */
PB_STATIC_ASSERT(sizeof(double) == 8, DOUBLE_MUST_BE_8_BYTES)
#endif

