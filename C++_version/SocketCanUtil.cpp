#include "SocketCanUtil.h"

SocketCanUtil::SocketCanUtil()
{

}

int SocketCanUtil::init_socket(string interface_name)
{
    socket_fd = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    
    strcpy(ifr.ifr_name, "can0" );
    ioctl(socket_fd, SIOCGIFINDEX, &ifr);

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    bind(socket_fd, (sockaddr*)&addr, sizeof(addr));

    return 0; // TODO: return some other value/catch exception if get socket error upon creation
}

void SocketCanUtil::make_socket_can_frame(uint8_t can_id, uint8_t* data, uint8_t data_size, can_frame* frame)
{
    frame->can_id = can_id;
    frame->can_dlc = data_size;
    memcpy(&(frame->data), data, data_size);
}

int SocketCanUtil::send_frame(can_frame* frame)
{
    printf("Sending Frame\n");
    int num_bytes = write(socket_fd, frame, sizeof(can_frame));
    if(num_bytes != sizeof(can_frame))
    {
        perror("Write");
    }
}

int SocketCanUtil::get_frame(can_frame* frame)
{
    printf("Receiving Frame\n");
    int num_bytes = read(socket_fd, frame, sizeof(struct can_frame));
    if(num_bytes != sizeof(can_frame))
    {
        perror("Read");
    }
}

void SocketCanUtil::print_frame(can_frame* frame)
{
    printf("\ncan_id: %02X\t", frame->can_id);
    printf("data:\t");
    for(int i = 0; i < frame->can_dlc; i++)
    {
        printf("%02X ", frame->data[i]);
    }
}