#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>

static int
query_interface_mac_address(int sock, char *buf, unsigned int size)
{
  struct ifreq req[1];
  int i = 0, j = 0;

  while (++ i) {
    
    memset(req, 0, sizeof(struct ifreq));
    req->ifr_ifindex = i;

    if (ioctl(sock, SIOCGIFNAME, req) < 0) {
      // perror("SIOCGIFNAME");
      break;
    }
    
    if (!(ioctl(sock, SIOCGIFFLAGS, req) < 0) && !(req->ifr_flags & IFF_LOOPBACK)) {
        
      if(ioctl(sock, SIOCGIFHWADDR, req) < 0) {
        perror("SIOCGIFHWADDR");
        return -1;
      }

      snprintf(buf + j * 18, size, "%02x:%02x:%02x:%02x:%02x:%02x.",
               (unsigned char)req[0].ifr_hwaddr.sa_data[0],
               (unsigned char)req[0].ifr_hwaddr.sa_data[1],
               (unsigned char)req[0].ifr_hwaddr.sa_data[2],
               (unsigned char)req[0].ifr_hwaddr.sa_data[3],
               (unsigned char)req[0].ifr_hwaddr.sa_data[4],
               (unsigned char)req[0].ifr_hwaddr.sa_data[5]);
      size -= 18;
      j ++;
    }
  };

  buf[j * 18 - 1] = 0;
  return 0;
}

int
get_multi_mac(char *buf, size_t size)
{
  int ret;
  int sock = socket (AF_INET, SOCK_DGRAM, 0);
  if (sock < 0) {
    perror("socket");
    return -1;
  }

  ret = query_interface_mac_address(sock, buf, size);
  
  close(sock);
  return ret;
}

#ifdef APP
int main(int argc, char *argv[])
{
  char buf[1024];
  size_t size = 1024;
  if (get_multi_mac(buf, size) == 0) {
    printf("All Mac Addresses:\n%s\n", buf);
  }
  return 0;
}
#endif
