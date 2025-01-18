#include <fcntl.h>
#include <unistd.h>

int main() {
    int fd = open("/dev/ttyUSB0", O_WRONLY);
    unsigned char data1[] = {0xA0, 0x01, 0x01, 0xA2};
    unsigned char data2[] = {0xA0, 0x01, 0x00, 0xA1};
    write(fd, data1, sizeof(data1));
    sleep(1);
    write(fd, data2, sizeof(data2));
    close(fd);
    usleep(300000);
    return 0;
}
