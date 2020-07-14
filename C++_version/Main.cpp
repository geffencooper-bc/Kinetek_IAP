#include "SocketCanUtil.h"

int test_can();

int main()
{
    SocketCanUtil ut = SocketCanUtil();
    ut.init_socket("can0");
    
    
    // test_can();
}

int test_can()
{
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    struct sockaddr_can addr;
    struct ifreq ifr;

    strcpy(ifr.ifr_name, "can0" );
    ioctl(s, SIOCGIFINDEX, &ifr);

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    bind(s, (struct sockaddr *)&addr, sizeof(addr));

    struct can_frame frame;
    printf("size: %i:", sizeof(can_frame));

    while(true)
    {
        int nbytes = read(s, &frame, sizeof(struct can_frame));

        if (nbytes < 0) {
                perror("can raw socket read");
                return 1;
        }

        /* paranoid check ... */
        if (nbytes < sizeof(struct can_frame)) {
                fprintf(stderr, "read: incomplete CAN frame\n");
                return 1;
        }

        // printf("Received a CAN frame from interface %s", ifr.ifr_name);
        printf("\ncan_id: %02X\t", frame.can_id);
        printf("data:\t");
        for(int i = 0; i < frame.can_dlc; i++)
        {
            printf("%02X ", frame.data[i]);
        }
    }
}
